"""
可信计算核心统一入口（TEE 兼容）

SecureCore 是整个可信计算核心对外暴露的唯一接口。
外部模块（路由层、服务层）只通过此类访问检测能力，
不直接接触 FallDetector、RiskEngine 等内部组件。

数据流规则：
  - 原始帧只能进入 SecureCore，不进入普通业务层
  - SecureCore 对外只输出 SecureFrameResult（已模糊帧 + 风险结果 + 事件摘要）
  - 数据库和日志只存事件摘要，不存原始视频
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional

from .types import SecureFrameResult
from .fall_detector import FallDetector
from .risk_engine import RiskEngine, risk_engine as _global_risk_engine
from .frame_ingest import FrameIngestor
from .event_builder import EventBuilder
from .integrity import compute_core_hash, verify_integrity
from .model_loader import ModelLoader

logger = logging.getLogger('secure_core')


class SecureCore:
    """
    可信计算核心（TEE 兼容原型）

    将视频解码、匿名化、检测、追踪、风险判定和事件摘要生成
    封装为独立单元，未来可直接迁移到 Open Enclave / Confidential VM。

    使用方式:
        core = SecureCore()
        core.initialize()                          # 启动校验

        info = core.start_session(is_live=True, user_id=1)
        result = await core.process_frame_async(info["session_id"], frame)
        core.close_session(info["session_id"])
    """

    def __init__(self):
        self._model_loader = ModelLoader()
        self._frame_ingestor = FrameIngestor()
        self._event_builder = EventBuilder()
        self._detector: Optional[FallDetector] = None
        # 使用 risk_engine 模块级单例，确保 fall_detector 的 lazy import 引用同一实例
        self._risk_engine: RiskEngine = _global_risk_engine
        self._core_hash: str = ""
        self._model_hash: str = ""
        self._model_version: str = "fall_v5"
        self._initialized: bool = False

    # ==================== 生命周期 ====================

    def initialize(self, whitelist: Dict = None) -> dict:
        """
        启动时初始化：校验完整性 + 加载模型

        Args:
            whitelist: 哈希白名单配置（开发阶段可为 None，跳过校验）

        Returns:
            初始化状态信息

        Raises:
            RuntimeError: 完整性校验失败
        """
        # 1. 计算核心代码哈希
        self._core_hash = compute_core_hash()
        logger.info(f"核心代码哈希: {self._core_hash[:16]}...")

        # 2. 计算模型哈希
        self._model_hash = self._model_loader.get_model_hash()
        logger.info(f"模型文件哈希: {self._model_hash[:16]}...")

        # 3. 校验白名单（如果提供）
        if whitelist is not None:
            if not verify_integrity(self._core_hash, self._model_hash, whitelist):
                raise RuntimeError(
                    "完整性校验失败：核心代码或模型哈希不在白名单中"
                )
            logger.info("完整性校验通过")

        # 4. 加载检测模型
        model_path = self._model_loader.get_model_path()
        self._detector = FallDetector(model_path=model_path)
        self._initialized = True

        logger.info("SecureCore 初始化完成")
        return {
            "core_hash": self._core_hash,
            "model_hash": self._model_hash,
            "model_version": self._model_version,
            "status": "trusted-ready",
        }

    # ==================== 会话管理 ====================

    def start_session(
        self,
        is_live: bool = False,
        user_id: Optional[int] = None,
    ) -> dict:
        """
        创建检测会话

        Args:
            is_live: 是否为实时摄像头流
            user_id: 用户ID（用于加载个性化检测配置）

        Returns:
            {"session_id", "core_hash", "model_version", "status"}
        """
        self._ensure_initialized()

        session_id = self._detector.create_session()
        self._risk_engine.create_session(session_id, is_live=is_live, user_id=user_id)

        return {
            "session_id": session_id,
            "core_hash": self._core_hash,
            "model_version": self._model_version,
            "status": "trusted-ready",
        }

    def close_session(self, session_id: str, now: Optional[float] = None) -> List:
        """
        关闭检测会话，返回所有未结束事件的变更

        Args:
            session_id: 会话ID
            now: 当前时间戳

        Returns:
            ended EventChange 列表
        """
        if not self._initialized:
            return []

        if now is None:
            now = time.time()

        # 风险引擎关闭（返回未结束事件）
        ended_changes = self._risk_engine.close_session(session_id, now=now)

        # 检测器关闭（清理追踪状态）
        self._detector.close_session(session_id)

        # 清理事件构建器的会话缓存
        self._event_builder.clear_session(session_id)

        return ended_changes

    # ==================== 帧处理 ====================

    def process_frame(
        self,
        session_id: str,
        frame,
        timestamp_ms: Optional[int] = None,
    ) -> SecureFrameResult:
        """
        处理单帧（同步）

        这是可信核心的主处理链路：
          帧校验 → 检测 + 追踪 + 人脸模糊 → 风险判定 → 输出结果

        Args:
            session_id: 会话ID
            frame: BGR numpy 数组
            timestamp_ms: 帧时间戳（可选）

        Returns:
            SecureFrameResult: 包含已模糊帧、风险结果、事件变更
        """
        self._ensure_initialized()

        # 1. 帧输入校验
        self._frame_ingestor.validate(frame)

        # 2. 检测 + 追踪 + 人脸模糊
        result = self._detector.process_frame(session_id, frame)

        # 3. 风险判定
        now = time.time()
        risk_results, event_changes = self._risk_engine.process(
            session_id, result.frame_result.persons, now
        )

        return SecureFrameResult(
            processed_frame=result.processed_frame,
            risk_results=risk_results,
            event_changes=event_changes,
            core_hash=self._core_hash,
            model_version=self._model_version,
        )

    async def process_frame_async(
        self,
        session_id: str,
        frame,
        timestamp_ms: Optional[int] = None,
    ) -> SecureFrameResult:
        """处理单帧（异步版本）"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.process_frame, session_id, frame, timestamp_ms
        )

    # ==================== 透传接口 ====================

    def get_user_id(self, session_id: str) -> Optional[int]:
        """获取会话关联的用户ID"""
        return self._risk_engine.get_user_id(session_id)

    @property
    def session_manager(self):
        """访问内部 SessionManager（兼容现有代码）"""
        return self._detector.session_manager if self._detector else None

    @property
    def core_hash(self) -> str:
        """当前核心代码哈希"""
        return self._core_hash

    @property
    def model_version(self) -> str:
        """当前模型版本"""
        return self._model_version

    @property
    def event_builder(self) -> EventBuilder:
        """事件构建器（用于构建匿名化事件摘要）"""
        return self._event_builder

    # ==================== 内部方法 ====================

    def _ensure_initialized(self):
        if not self._initialized:
            raise RuntimeError("SecureCore 未初始化，请先调用 initialize()")

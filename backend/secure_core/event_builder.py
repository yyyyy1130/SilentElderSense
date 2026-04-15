"""
事件摘要构建模块

将 risk_engine 输出的 EventChange 构造为标准化的事件摘要 JSON。
此模块是 TEE 与外部世界的数据边界：
  - 原始追踪 ID 映射为匿名 ID
  - 只保留必要字段对外输出
"""
from typing import Dict, List, Optional
from .risk_engine import EventChange


class EventBuilder:
    """事件摘要构建器"""

    def __init__(self):
        # 会话级 person_id 计数器（用于匿名映射）
        self._person_map: Dict[str, Dict[int, str]] = {}  # session_id -> {raw_id -> anon_id}

    def build_event_summary(
        self,
        event_change: EventChange,
        session_id: str,
        core_hash: str = "",
        model_version: str = "",
    ) -> dict:
        """
        将单条 EventChange 构造为事件摘要 JSON

        Args:
            event_change: 风险引擎的事件变更信号
            session_id: 会话ID
            core_hash: 当前核心代码哈希
            model_version: 模型版本

        Returns:
            标准化的事件摘要字典
        """
        anon_id = self._anonymize_person_id(session_id, event_change.person_id)

        return {
            "session_id": session_id,
            "event_type": event_change.event_type,
            "risk_level": event_change.risk_level,
            "anon_person_id": anon_id,
            "start_ts": event_change.start_ts,
            "end_ts": event_change.end_ts,
            "frame_count": event_change.frame_count,
            "core_hash": core_hash,
            "model_version": model_version,
        }

    def build_batch_summaries(
        self,
        event_changes: List[EventChange],
        session_id: str,
        core_hash: str = "",
        model_version: str = "",
    ) -> List[dict]:
        """批量构建事件摘要"""
        return [
            self.build_event_summary(ch, session_id, core_hash, model_version)
            for ch in event_changes
        ]

    @staticmethod
    def anonymize_id(raw_id: int) -> str:
        """
        将原始追踪 ID 映射为匿名 ID（无状态，确定性）

        例如: ByteTrack ID 3 → "p03"
        """
        return f"p{raw_id:02d}"

    def _anonymize_person_id(self, session_id: str, raw_id: int) -> str:
        """
        将原始追踪 ID 映射为匿名 ID

        映射关系在同一会话内保持一致。
        例如: ByteTrack ID 3 → "p03"
        """
        if session_id not in self._person_map:
            self._person_map[session_id] = {}

        session_map = self._person_map[session_id]
        if raw_id not in session_map:
            session_map[raw_id] = f"p{raw_id:02d}"

        return session_map[raw_id]

    def get_anon_id(self, session_id: str, raw_id: int) -> str:
        """获取已映射的匿名 ID（用于事件详情页等场景）"""
        session_map = self._person_map.get(session_id, {})
        return session_map.get(raw_id, f"p{raw_id:02d}")

    def clear_session(self, session_id: str):
        """会话结束后清理映射缓存"""
        self._person_map.pop(session_id, None)

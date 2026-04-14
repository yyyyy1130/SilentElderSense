"""
可信计算核心（TEE 兼容）

将视频解码、匿名化、检测、追踪、风险判定和事件摘要生成
封装为独立模块。当前为 TEE 兼容原型，正式部署可迁移到
Open Enclave / Confidential VM / Azure Attestation 环境。

接口:
    SecureCore              - 统一入口类
    start_session()         - 创建检测会话
    process_frame()         - 处理单帧（同步）
    process_frame_async()   - 处理单帧（异步）
    close_session()         - 关闭会话
"""

from .enclave_api import SecureCore
from .types import PersonResult, FrameResult, SessionResult, SecureFrameResult

__all__ = [
    'SecureCore',
    'PersonResult',
    'FrameResult',
    'SessionResult',
    'SecureFrameResult',
]

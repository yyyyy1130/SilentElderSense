"""
数据类型定义
"""
from dataclasses import dataclass
from typing import Optional, List
import numpy as np


@dataclass
class PersonResult:
    """单个人的检测结果"""
    person_id: int                      # 追踪ID (ByteTrack)
    class_id: int                       # 0=normal, 1=fallen
    class_name: str                     # "normal" / "fallen"
    confidence: float                   # 置信度
    box: List[float]                    # [x1, y1, x2, y2]
    movement: Optional[float] = None    # 相比上一帧的位移（像素），首帧为 None


@dataclass
class FrameResult:
    """单帧检测结果（多人）"""
    detected: bool                      # 是否检测到任何人
    persons: List[PersonResult]         # 检测到的所有人


@dataclass
class SessionResult:
    """会话处理结果"""
    video_id: str
    frame_result: FrameResult
    processed_frame: Optional[np.ndarray] = None  # 人脸模糊后的帧


@dataclass
class SecureFrameResult:
    """secure_core 对外输出的单帧处理结果

    TEE 边界外的模块只接收此结构，不接触原始帧或内部追踪数据。
    """
    processed_frame: Optional[np.ndarray]  # 人脸模糊后的帧（可展示）
    risk_results: List                     # PersonRisk 列表
    event_changes: List                    # EventChange 列表
    core_hash: str = ""
    model_version: str = ""

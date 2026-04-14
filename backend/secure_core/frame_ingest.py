"""
帧输入校验模块

对进入可信核心的原始帧做基本校验，
防止异常输入导致后续处理出错。
"""
import numpy as np


class FrameIngestor:
    """帧输入校验器"""

    MAX_FRAME_SIZE = 5 * 1024 * 1024  # 5MB
    MIN_FRAME_DIM = 16                # 最小帧尺寸

    def validate(self, frame) -> None:
        """
        校验帧数据

        Args:
            frame: numpy 数组（BGR 图像）或 bytes（JPEG 字节流）

        Raises:
            ValueError: 帧数据不合法
        """
        if frame is None:
            raise ValueError("帧数据为空")

        if isinstance(frame, bytes):
            if len(frame) == 0:
                raise ValueError("帧字节流为空")
            if len(frame) > self.MAX_FRAME_SIZE:
                raise ValueError(f"帧大小超过限制 ({self.MAX_FRAME_SIZE // 1024 // 1024}MB)")
            return

        if isinstance(frame, np.ndarray):
            if frame.size == 0:
                raise ValueError("帧数组为空")
            if frame.ndim < 2:
                raise ValueError(f"帧维度异常: {frame.ndim}")
            h, w = frame.shape[:2]
            if h < self.MIN_FRAME_DIM or w < self.MIN_FRAME_DIM:
                raise ValueError(f"帧尺寸过小: {w}x{h} (最小 {self.MIN_FRAME_DIM})")
            return

        raise TypeError(f"不支持的帧类型: {type(frame)}")

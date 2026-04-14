"""
模型加载模块

当前版本直接加载明文模型文件。
未来可扩展为：加密存储 → 启动校验通过后解密 → 内存中加载。

此模块体现"可信环境放行后才拿到关键资产"的设计思想。
"""
from pathlib import Path
from typing import Optional

# secure_core 包目录
_PKG_ROOT = Path(__file__).parent

# 默认模型路径
DEFAULT_DETECTION_MODEL = str(_PKG_ROOT / "models" / "fall_detection_v5.onnx")
DEFAULT_FACE_MODEL = str(_PKG_ROOT / "models" / "blaze_face_full_range.tflite")


class ModelLoader:
    """
    模型加载器

    当前版本：
      - get_model_path() 直接返回原始路径
      - get_model_hash() 计算模型文件哈希

    未来扩展：
      - 模型文件加密存储 (.onnx.enc)
      - 启动校验通过后从环境变量获取密钥
      - 解密后仅在内存中加载，不落盘
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: 检测模型路径，默认 core/models/fall_detection_v5.onnx
        """
        self.model_path = model_path or DEFAULT_DETECTION_MODEL

    def get_model_path(self) -> str:
        """
        获取模型路径

        当前直接返回原始路径。
        未来可改为：解密到内存/临时文件后返回可用路径。
        """
        return self.model_path

    def get_model_hash(self) -> str:
        """计算模型文件的 SHA-256"""
        from .integrity import sha256_file
        return sha256_file(self.model_path)

    @staticmethod
    def get_default_model_path() -> str:
        """获取默认检测模型路径"""
        return DEFAULT_DETECTION_MODEL

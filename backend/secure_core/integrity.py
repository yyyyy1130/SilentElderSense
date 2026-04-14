"""
完整性校验模块（原型级 attestation）

启动时对 secure_core 关键代码和模型文件计算 SHA-256 哈希，
与配置中的白名单比对，校验通过才允许服务启动。

此模块是"原型级远程证明"的软件实现：
  - 验证"运行的是谁"（代码哈希）
  - 验证"模型是不是那份模型"（模型哈希）
  - 只有通过验证才放行

正式部署可接入 Open Enclave / Azure Attestation。
"""
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

# secure_core 内需要校验的关键文件
_CORE_DIR = Path(__file__).parent
CORE_FILES: List[str] = [
    str(_CORE_DIR / "enclave_api.py"),
    str(_CORE_DIR / "anonymizer.py") if (_CORE_DIR / "anonymizer.py").exists() else None,
    str(_CORE_DIR / "fall_detector.py"),
    str(_CORE_DIR / "session.py"),
    str(_CORE_DIR / "risk_engine.py"),
    str(_CORE_DIR / "event_builder.py"),
    str(_CORE_DIR / "frame_ingest.py"),
    str(_CORE_DIR / "integrity.py"),
    str(_CORE_DIR / "model_loader.py"),
]
# 过滤不存在的文件（如 anonymizer.py 可能还未创建）
CORE_FILES = [f for f in CORE_FILES if f is not None]


def sha256_file(path: str) -> str:
    """计算单个文件的 SHA-256"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_core_hash() -> str:
    """
    对 secure_core 关键代码文件计算聚合哈希

    Returns:
        SHA-256 hex string
    """
    h = hashlib.sha256()
    for path in sorted(CORE_FILES):
        try:
            h.update(sha256_file(path).encode("utf-8"))
        except FileNotFoundError:
            continue
    return h.hexdigest()


def compute_model_hash(model_path: str) -> str:
    """对模型文件计算 SHA-256"""
    return sha256_file(model_path)


def verify_integrity(
    core_hash: str,
    model_hash: str,
    whitelist: Dict,
) -> bool:
    """
    校验核心代码和模型哈希是否在白名单中

    Args:
        core_hash: 当前核心代码聚合哈希
        model_hash: 当前模型文件哈希
        whitelist: 白名单配置，格式:
            {
                "trusted_core_hashes": ["abc123...", ...],
                "trusted_model_hashes": ["def456...", ...]
            }

    Returns:
        True 表示校验通过
    """
    trusted_core = whitelist.get("trusted_core_hashes", [])
    trusted_model = whitelist.get("trusted_model_hashes", [])

    if not trusted_core and not trusted_model:
        # 白名单为空时跳过校验（开发阶段）
        return True

    core_ok = core_hash in trusted_core if trusted_core else True
    model_ok = model_hash in trusted_model if trusted_model else True

    return core_ok and model_ok

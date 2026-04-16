import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATA_DIR, "db.sqlite3")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 差分隐私配置
    DP_DEFAULT_EPSILON = 0.8  # 默认 epsilon
    DP_DAILY_LIMIT = 3.0  # 每用户每日隐私预算上限


class DevelopmentConfig(Config):
    """开发环境配置 - 数据加噪但不限制预算"""
    DEBUG = True
    DP_BUDGET_ENABLED = False  # 禁用预算计算，数据仍加噪


class ProductionConfig(Config):
    """生产环境配置 - 数据加噪并限制预算"""
    DEBUG = False
    DP_BUDGET_ENABLED = True  # 启用预算计算

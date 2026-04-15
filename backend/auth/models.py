from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    def set_password(self, password):
        """密码加密"""
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


# 数据库引擎和会话
engine = None
SessionLocal = None


def init_db(app):
    global engine, SessionLocal
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(database_url, echo=True)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    # SQLite 迁移：为已有 events 表添加新列
    _migrate_events_table(engine)

    # 创建默认管理员账户
    db = SessionLocal()
    try:
        admin = db.query(User).filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('123456')
            db.add(admin)
            db.commit()
            print("已创建默认管理员: admin / 123456")
    except Exception as e:
        print(f"创建默认管理员失败: {e}")
        db.rollback()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_events_table(engine):
    """为 events 表添加 TEE 相关字段（安全忽略已存在的列）"""
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if 'events' not in insp.get_table_names():
        return
    existing = {col['name'] for col in insp.get_columns('events')}
    new_columns = [
        ('core_hash', 'VARCHAR(64)'),
        ('model_version', 'VARCHAR(32)'),
        ('anon_person_id', 'VARCHAR(16)'),
        ('feature_summary', 'TEXT'),
    ]
    with engine.connect() as conn:
        for col_name, col_type in new_columns:
            if col_name not in existing:
                conn.execute(text(f'ALTER TABLE events ADD COLUMN {col_name} {col_type}'))
        conn.commit()
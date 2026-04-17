from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt

Base = declarative_base()

VALID_ROLES = {'user', 'admin', 'platform'}


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String(20), default='user')
    platform_org_id = Column(Integer, nullable=True)
    community_group_id = Column(Integer, nullable=True)
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

    # SQLite 迁移
    _migrate_events_table(engine)
    _migrate_users_role(engine)
    _migrate_users_org(engine)

    # 创建默认管理员账户
    db = SessionLocal()
    try:
        admin = db.query(User).filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                role='admin'
            )
            admin.set_password('123456')
            db.add(admin)
            db.commit()
            print("已创建默认管理员: admin / 123456")
        elif admin.role != 'admin':
            admin.role = 'admin'
            db.commit()
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


def _migrate_users_role(engine):
    """为 users 表添加 role 字段，并将 is_admin 同步到 role"""
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if 'users' not in insp.get_table_names():
        return
    existing = {col['name'] for col in insp.get_columns('users')}

    with engine.connect() as conn:
        # 添加 role 列
        if 'role' not in existing:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
            conn.commit()

        # 将 is_admin=True 的用户同步为 role='admin'
        conn.execute(text("UPDATE users SET role = 'admin' WHERE is_admin = 1 AND (role IS NULL OR role = 'user')"))
        # 确保所有用户都有 role 值
        conn.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL"))
        conn.commit()


def _migrate_users_org(engine):
    """为 users 表添加 platform_org_id 和 community_group_id 字段"""
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if 'users' not in insp.get_table_names():
        return
    existing = {col['name'] for col in insp.get_columns('users')}
    with engine.connect() as conn:
        if 'platform_org_id' not in existing:
            conn.execute(text('ALTER TABLE users ADD COLUMN platform_org_id INTEGER'))
        if 'community_group_id' not in existing:
            conn.execute(text('ALTER TABLE users ADD COLUMN community_group_id INTEGER'))
        conn.commit()
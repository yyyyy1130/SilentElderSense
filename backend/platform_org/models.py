from sqlalchemy import Column, Integer, String, Text, DateTime, inspect, text
from datetime import datetime
from auth.models import Base, engine as get_engine


class CommunityGroup(Base):
    __tablename__ = 'community_groups'

    id = Column(Integer, primary_key=True)
    platform_user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(256), nullable=True)
    status = Column(String(16), default='active')  # active, suspended
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'platform_user_id': self.platform_user_id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


def _migrate_community_platform_user(engine):
    """community_groups: 从 platform_org_id 迁移到 platform_user_id"""
    insp = inspect(engine)
    if 'community_groups' not in insp.get_table_names():
        return
    existing = {col['name'] for col in insp.get_columns('community_groups')}
    with engine.connect() as conn:
        # 添加 platform_user_id 列
        if 'platform_user_id' not in existing:
            conn.execute(text('ALTER TABLE community_groups ADD COLUMN platform_user_id INTEGER'))
            conn.commit()
            # 从旧 platform_orgs + users 回填
            tables = insp.get_table_names()
            if 'platform_orgs' in tables and 'platform_org_id' in existing:
                conn.execute(text("""
                    UPDATE community_groups SET platform_user_id = (
                        SELECT users.id FROM users
                        WHERE users.platform_org_id = community_groups.platform_org_id
                        AND users.role = 'platform'
                        LIMIT 1
                    )
                    WHERE platform_user_id IS NULL
                """))
                conn.commit()

        # SQLite 不支持 DROP COLUMN，但可以重建表
        # 检查是否需要重建（platform_org_id 是否有 NOT NULL 约束）
        # 我们需要让 platform_org_id 变为 nullable
        if 'platform_org_id' in existing:
            # 重建表：去掉 platform_org_id 的 NOT NULL 约束
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS community_groups_new (
                    id INTEGER PRIMARY KEY,
                    platform_user_id INTEGER NOT NULL,
                    platform_org_id INTEGER,  -- nullable，保留旧数据兼容
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    address VARCHAR(256),
                    status VARCHAR(16) DEFAULT 'active',
                    created_at DATETIME
                )
            """))
            conn.execute(text("""
                INSERT INTO community_groups_new
                SELECT id, platform_user_id, platform_org_id, name, description, address, status, created_at
                FROM community_groups
            """))
            conn.execute(text("DROP TABLE community_groups"))
            conn.execute(text("ALTER TABLE community_groups_new RENAME TO community_groups"))
            conn.commit()

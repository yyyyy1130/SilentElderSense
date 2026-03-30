"""
模拟数据生成脚本

生成测试用户和模拟事件数据，模拟真实检测逻辑的写入方式
"""
import os
import sys
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATA_DIR
from auth.models import Base, User
from events.models import Event

DB_NAME = "db.sqlite3"
db_path = os.path.join(DATA_DIR, DB_NAME)

# 创建引擎和会话
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
db = Session()


def random_datetime_in_range(start_dt: datetime, end_dt: datetime) -> datetime:
    """生成指定时间范围内的随机时间"""
    delta = end_dt - start_dt
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_dt + timedelta(seconds=random_seconds)


def generate_users():
    """生成两个测试用户：admin 和 test"""
    print("[1/2] 生成用户...")

    users = []

    # 检查并创建 admin 用户（基础用户，无事件数据）
    admin = db.query(User).filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('123456')
        db.add(admin)
    users.append(admin)

    # 检查并创建 test 用户（测试用户，包含所有事件数据）
    test = db.query(User).filter_by(username='test').first()
    if not test:
        test = User(
            username='test',
            email='test@example.com',
            is_admin=False
        )
        test.set_password('123456')
        db.add(test)
    users.append(test)

    db.commit()
    print("      已准备用户: admin, test (密码均为 123456)")
    return users


def generate_events(test_user, count=None, days_back=7):
    """
    为 test 用户生成事件数据，模拟真实检测逻辑

    参数:
        test_user: 测试用户对象
        count: 事件总数（None 则随机 100-200）
        days_back: 时间跨度（天数），以当前时间为最后事件时间

    事件类型与风险等级对应：
      FALLEN:         LOW(不可能), MEDIUM(连续5帧), HIGH(持续≥1s)
      STILLNESS:      LOW(30s静止), MEDIUM(持续≥60s)
      NIGHT_ABNORMAL: MEDIUM(夜间+静止+实时流)

    时间分布：所有事件类型均在 24 小时内随机分布
    """
    # 随机事件总数（100-200）
    if count is None:
        count = random.randint(100, 200)

    print(f"[2/2] 为 test 用户生成 {count} 条事件（过去 {days_back} 天）...")

    # 时间范围：过去 days_back 天，以当前时间为结束点
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days_back)

    # 事件类型（与实际检测逻辑一致）
    event_types = ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']

    # 处理状态分布
    statuses = ['pending', 'confirmed', 'false_alarm']
    status_weights = [0.3, 0.5, 0.2]  # 30%待处理, 50%已确认, 20%误报

    events = []

    # 随机分配事件类型数量（不均分）
    # 使用随机权重，确保每种类型至少有少量数据
    type_weights = [random.uniform(0.15, 0.5) for _ in range(3)]
    total_weight = sum(type_weights)
    type_weights = [w / total_weight for w in type_weights]

    counts_per_type = [int(count * w) for w in type_weights]
    # 将余数分配给随机一个类型
    remainder = count - sum(counts_per_type)
    if remainder > 0:
        counts_per_type[random.randint(0, 2)] += remainder

    print(f"      事件类型分布: FALLEN={counts_per_type[0]}, STILLNESS={counts_per_type[1]}, NIGHT_ABNORMAL={counts_per_type[2]}")

    # 预生成所有事件时间
    event_times = []

    # 生成 FALLEN 事件时间（随机分布在7天内）
    for _ in range(counts_per_type[0]):
        event_times.append(('FALLEN', random_datetime_in_range(start_dt, end_dt)))

    # 生成 STILLNESS 事件时间（随机分布在7天内）
    for _ in range(counts_per_type[1]):
        event_times.append(('STILLNESS', random_datetime_in_range(start_dt, end_dt)))

    # 生成 NIGHT_ABNORMAL 事件时间（24小时随机分布）
    for _ in range(counts_per_type[2]):
        event_times.append(('NIGHT_ABNORMAL', random_datetime_in_range(start_dt, end_dt)))

    # 按时间排序，确保最后的事件接近当前时间
    event_times.sort(key=lambda x: x[1])

    for i, (event_type, start_time) in enumerate(event_times):
        # 根据事件类型确定风险等级和持续时间
        if event_type == 'FALLEN':
            # 跌倒：MEDIUM 或 HIGH，持续时间较短
            risk_level = random.choices(['MEDIUM', 'HIGH'], weights=[0.4, 0.6])[0]
            duration_secs = random.uniform(2.0, 15.0)  # 跌倒持续2-15秒
        elif event_type == 'STILLNESS':
            # 静止：LOW 或 MEDIUM，持续时间较长
            risk_level = random.choices(['LOW', 'MEDIUM'], weights=[0.5, 0.5])[0]
            duration_secs = random.uniform(30.0, 300.0)  # 静止持续30秒-5分钟
        else:  # NIGHT_ABNORMAL
            # 夜间异常：固定 MEDIUM
            risk_level = 'MEDIUM'
            duration_secs = random.uniform(60.0, 180.0)  # 夜间异常持续1-3分钟

        # 结束时间
        end_time = start_time + timedelta(seconds=duration_secs)

        # 帧数估算（假设 25fps，取整）
        fps = 25
        frame_count = int(duration_secs * fps * random.uniform(0.8, 1.2))

        # 模拟视频会话ID和人员ID
        video_id = f"vid_{random.randint(1000, 9999)}"
        person_id = random.randint(0, 3)  # 常见场景：0-3人

        # 处理状态
        status = random.choices(statuses, weights=status_weights)[0]

        # 备注（模拟人工处理记录）
        notes_map = {
            'pending': '',
            'confirmed': random.choice(['已确认', '已通知家属', '已处理']),
            'false_alarm': random.choice(['误报', '宠物活动', '光线变化'])
        }

        event = Event(
            user_id=test_user.id,
            video_id=video_id,
            person_id=person_id,
            event_type=event_type,
            risk_level=risk_level,
            start_time=start_time,
            end_time=end_time,
            frame_count=frame_count,
            status=status,
            notes=notes_map[status]
        )
        db.add(event)
        events.append(event)

        if (i + 1) % 10 == 0:
            print(f"      进度: {i+1}/{count}")

    db.commit()
    print(f"      已生成 {len(events)} 条事件")
    print(f"      时间范围: {start_dt.strftime('%Y-%m-%d %H:%M')} ~ {end_dt.strftime('%Y-%m-%d %H:%M')}")
    return events


def print_summary():
    """打印数据统计"""
    print("\n" + "="*50)
    print("数据生成完成！统计如下：")
    print("="*50)

    user_count = db.query(User).count()
    event_count = db.query(Event).count()

    print(f"  用户数量:       {user_count}")
    print(f"  事件数量:       {event_count}")

    # 用户列表
    print("\n用户列表:")
    for user in db.query(User).all():
        event_cnt = db.query(Event).filter(Event.user_id == user.id).count()
        print(f"  {user.username} / 123456 - {event_cnt} 条事件")

    # 时间范围
    first_event = db.query(Event).order_by(Event.start_time.asc()).first()
    last_event = db.query(Event).order_by(Event.start_time.desc()).first()
    if first_event and last_event:
        print(f"\n时间范围:")
        print(f"  最早事件: {first_event.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  最新事件: {last_event.start_time.strftime('%Y-%m-%d %H:%M')}")

    # 事件类型分布
    print("\n事件类型分布:")
    for event_type in ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']:
        count = db.query(Event).filter(Event.event_type == event_type).count()
        print(f"  {event_type}: {count}")

    # 风险等级分布
    print("\n风险等级分布:")
    for risk_level in ['HIGH', 'MEDIUM', 'LOW']:
        count = db.query(Event).filter(Event.risk_level == risk_level).count()
        print(f"  {risk_level}: {count}")

    # 处理状态分布
    print("\n处理状态分布:")
    for status in ['pending', 'confirmed', 'false_alarm']:
        count = db.query(Event).filter(Event.status == status).count()
        print(f"  {status}: {count}")

    print("\n" + "="*50)


def clear_mock_data():
    """清空模拟数据（保留用户）"""
    print("[0/2] 清空已有事件数据...")
    db.query(Event).delete()
    db.commit()
    print("      已清空事件数据")


def main():
    """主函数"""
    print("="*50)
    print("开始生成模拟数据...")
    print("="*50 + "\n")

    # 清空已有事件数据
    clear_mock_data()

    # 生成用户
    users = generate_users()
    test_user = users[1]  # test 用户

    # 为 test 用户生成事件（过去7天，数量随机100-200）
    generate_events(test_user, days_back=7)

    # 打印统计
    print_summary()

    db.close()


if __name__ == '__main__':
    main()
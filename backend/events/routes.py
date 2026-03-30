"""
事件 API 端点

接口:
    POST /api/events          - 记录事件
    GET  /api/events          - 查询事件列表
    GET  /api/events/<id>     - 获取事件详情
    PUT  /api/events/<id>     - 更新事件状态
"""
from datetime import datetime, timedelta
from quart import Blueprint, request, jsonify
from auth.models import get_db
from auth.utils import token_required
from .models import Event

events_bp = Blueprint('events', __name__)


@events_bp.route('/api/events', methods=['POST'])
@token_required
async def create_event():
    """
    记录事件

    请求体:
    {
        "video_id": "abc123",
        "person_id": 0,
        "event_type": "FALLEN",
        "risk_level": "HIGH",
        "start_time": "2024-03-23T10:00:00",
        "end_time": "2024-03-23T10:00:02",
        "duration": 2.0,
        "frame_count": 10
    }
    """
    user_id = request.current_user['user_id']
    data = await request.get_json()

    db = next(get_db())

    # 解析时间
    start_time = datetime.fromisoformat(data['start_time']) if isinstance(data['start_time'], str) else datetime.fromtimestamp(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time']) if isinstance(data['end_time'], str) else datetime.fromtimestamp(data['end_time'])

    event = Event(
        user_id=user_id,
        video_id=data['video_id'],
        person_id=data['person_id'],
        event_type=data['event_type'],
        risk_level=data['risk_level'],
        start_time=start_time,
        end_time=end_time,
        duration=data['duration'],
        frame_count=data.get('frame_count', 0),
        notes=data.get('notes')
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return jsonify({
        'message': '事件记录成功',
        'event': event.to_dict()
    }), 201


@events_bp.route('/api/events', methods=['GET'])
@token_required
async def list_events():
    """
    查询事件列表

    查询参数:
        event_type: 事件类型（可选）
        risk_level: 风险等级（可选）
        status: 状态（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        page: 页码（默认1）
        per_page: 每页数量（默认20）
    """
    user_id = request.current_user['user_id']
    db = next(get_db())

    # 构建查询，只返回当前用户的事件
    query = db.query(Event).filter(Event.user_id == user_id)

    event_type = request.args.get('event_type')
    if event_type:
        query = query.filter(Event.event_type == event_type)

    risk_level = request.args.get('risk_level')
    if risk_level:
        query = query.filter(Event.risk_level == risk_level)

    status = request.args.get('status')
    if status:
        query = query.filter(Event.status == status)

    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Event.start_time >= datetime.fromisoformat(start_date))

    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Event.end_time <= datetime.fromisoformat(end_date))

    # 分页
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    total = query.count()
    events = query.order_by(Event.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'events': [e.to_dict() for e in events]
    })


@events_bp.route('/api/events/<int:event_id>', methods=['GET'])
@token_required
async def get_event(event_id: int):
    """获取事件详情"""
    user_id = request.current_user['user_id']
    db = next(get_db())
    event = db.query(Event).filter_by(id=event_id, user_id=user_id).first()

    if not event:
        return jsonify({'error': '事件不存在'}), 404

    return jsonify({'event': event.to_dict()})


@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
@token_required
async def update_event(event_id: int):
    """
    更新事件状态

    请求体:
    {
        "status": "confirmed",  // pending, confirmed, false_alarm
        "notes": "已确认为误报"
    }
    """
    user_id = request.current_user['user_id']
    data = await request.get_json()

    db = next(get_db())
    event = db.query(Event).filter_by(id=event_id, user_id=user_id).first()

    if not event:
        return jsonify({'error': '事件不存在'}), 404

    if 'status' in data:
        event.status = data['status']
        event.handled_at = datetime.now()

    if 'notes' in data:
        event.notes = data['notes']

    db.commit()
    db.refresh(event)

    return jsonify({
        'message': '更新成功',
        'event': event.to_dict()
    })


@events_bp.route('/api/events/stats', methods=['GET'])
@token_required
async def event_stats():
    """
    事件统计

    查询参数:
        days: 统计天数（默认7）
    """
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))

    now = datetime.now()
    start_date = now - timedelta(days=days)

    db = next(get_db())

    # 本期事件
    current_events = db.query(Event).filter(
        Event.created_at >= start_date,
        Event.user_id == user_id
    ).all()

    # 上期事件（用于计算趋势）
    prev_start = start_date - timedelta(days=days)
    prev_events = db.query(Event).filter(
        Event.created_at >= prev_start,
        Event.created_at < start_date,
        Event.user_id == user_id
    ).all()

    # 本期统计
    stats = {
        'total': len(current_events),
        'by_type': {},
        'by_risk': {},
        'by_status': {}
    }

    # 上期统计（用于趋势计算）
    prev_stats = {
        'total': len(prev_events),
        'by_type': {},
        'by_risk': {},
        'by_status': {}
    }

    for event in current_events:
        if event.event_type not in stats['by_type']:
            stats['by_type'][event.event_type] = 0
        stats['by_type'][event.event_type] += 1

        if event.risk_level not in stats['by_risk']:
            stats['by_risk'][event.risk_level] = 0
        stats['by_risk'][event.risk_level] += 1

        if event.status not in stats['by_status']:
            stats['by_status'][event.status] = 0
        stats['by_status'][event.status] += 1

    for event in prev_events:
        if event.event_type not in prev_stats['by_type']:
            prev_stats['by_type'][event.event_type] = 0
        prev_stats['by_type'][event.event_type] += 1

        if event.risk_level not in prev_stats['by_risk']:
            prev_stats['by_risk'][event.risk_level] = 0
        prev_stats['by_risk'][event.risk_level] += 1

        if event.status not in prev_stats['by_status']:
            prev_stats['by_status'][event.status] = 0
        prev_stats['by_status'][event.status] += 1

    # 计算趋势
    def calc_trend(current, prev):
        if prev == 0:
            return None  # 上期为0，无法计算趋势
        return round((current - prev) / prev * 100, 1)

    trends = {
        'total': calc_trend(stats['total'], prev_stats['total']),
        'by_type': {},
        'by_risk': {},
        'by_status': {}
    }

    for event_type in stats['by_type']:
        current = stats['by_type'].get(event_type, 0)
        prev = prev_stats['by_type'].get(event_type, 0)
        trends['by_type'][event_type] = calc_trend(current, prev)

    for risk_level in stats['by_risk']:
        current = stats['by_risk'].get(risk_level, 0)
        prev = prev_stats['by_risk'].get(risk_level, 0)
        trends['by_risk'][risk_level] = calc_trend(current, prev)

    for status in stats['by_status']:
        current = stats['by_status'].get(status, 0)
        prev = prev_stats['by_status'].get(status, 0)
        trends['by_status'][status] = calc_trend(current, prev)

    stats['trends'] = trends

    # 计算确认率：已确认 / (已确认 + 误报)
    confirmed = stats['by_status'].get('confirmed', 0)
    false_alarm = stats['by_status'].get('false_alarm', 0)
    if confirmed + false_alarm > 0:
        stats['confirmation_rate'] = round(confirmed / (confirmed + false_alarm) * 100, 1)
    else:
        stats['confirmation_rate'] = None

    return jsonify(stats)


@events_bp.route('/api/events/hourly', methods=['GET'])
@token_required
async def hourly_trend():
    """
    小时级事件趋势（过去24小时）

    返回:
        {
            "hours": ["00:00", "01:00", ...],
            "by_type": {
                "FALLEN": [0, 1, 2, ...],
                "STILLNESS": [...],
                "NIGHT_ABNORMAL": [...]
            }
        }
    """
    user_id = request.current_user['user_id']
    db = next(get_db())

    now = datetime.now()
    start_time_threshold = now - timedelta(hours=24)

    events = db.query(Event).filter(
        Event.start_time >= start_time_threshold,
        Event.user_id == user_id
    ).all()

    # 直接使用数据库中的事件类型名称
    event_types = ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']

    # 初始化 24 小时的数据结构
    hours = [(now - timedelta(hours=23-i)).strftime('%H:00') for i in range(24)]
    hourly_data = {hour: {t: 0 for t in event_types} for hour in hours}

    for event in events:
        hour_key = event.start_time.strftime('%H:00')
        if hour_key in hourly_data and event.event_type in event_types:
            hourly_data[hour_key][event.event_type] += 1

    # 转换为前端需要的格式
    result = {
        'hours': hours,
        'by_type': {
            t: [hourly_data[h][t] for h in hours] for t in event_types
        }
    }

    return jsonify(result)


@events_bp.route('/api/events/daily', methods=['GET'])
@token_required
async def daily_trend():
    """
    每日事件趋势

    查询参数:
        days: 统计天数（默认7）

    返回:
        {
            "dates": ["03-24", "03-25", ...],
            "by_type": {
                "FALLEN": [2, 1, 3, ...],
                "STILLNESS": [...],
                "NIGHT_ABNORMAL": [...]
            }
        }
    """
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))
    db = next(get_db())

    now = datetime.now()
    start_date = (now - timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0)

    events = db.query(Event).filter(
        Event.start_time >= start_date,
        Event.user_id == user_id
    ).all()

    # 直接使用数据库中的事件类型名称
    event_types = ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']

    # 初始化每天的数据结构
    dates = []
    daily_data = {}
    for i in range(days):
        date = (now - timedelta(days=days-1-i)).strftime('%m-%d')
        dates.append(date)
        daily_data[date] = {t: 0 for t in event_types}

    for event in events:
        date_key = event.start_time.strftime('%m-%d')
        if date_key in daily_data and event.event_type in event_types:
            daily_data[date_key][event.event_type] += 1

    result = {
        'dates': dates,
        'by_type': {
            t: [daily_data[d][t] for d in dates] for t in event_types
        }
    }

    return jsonify(result)

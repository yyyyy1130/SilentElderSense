"""
平台组织与社区组 API

接口:
    POST   /api/platform/orgs                    - 创建平台组织（管理员）
    GET    /api/platform/orgs                    - 列表（管理员）
    PUT    /api/platform/orgs/<id>               - 更新（管理员）
    DELETE /api/platform/orgs/<id>               - 挂起（管理员）
    POST   /api/platform/orgs/<org_id>/groups    - 创建社区组（管理员）
    GET    /api/platform/orgs/<org_id>/groups    - 社区组列表（管理员）
    PUT    /api/platform/groups/<id>             - 更新社区组（管理员）
    DELETE /api/platform/groups/<id>             - 挂起社区组（管理员）
    GET    /api/platform/org                     - 当前平台用户所属组织
    GET    /api/platform/communities             - 当前组织下社区组列表
    GET    /api/platform/stats                   - 聚合统计（平台用户，强制 DP）
    GET    /api/platform/stats/daily             - 每日趋势（平台用户，强制 DP）
    GET    /api/community/groups                 - 可选社区组列表（普通用户）
    PUT    /api/user/community                   - 选择/切换社区组
    GET    /api/user/community                   - 获取当前绑定
"""
from datetime import datetime, timedelta
from quart import Blueprint, request, jsonify, current_app
from auth.models import get_db, User
from auth.utils import token_required, admin_required, role_required
from .models import PlatformOrg, CommunityGroup
from events.models import Event

platform_bp = Blueprint('platform', __name__)


# ── 管理员：平台组织 CRUD ──────────────────────────

@platform_bp.route('/api/platform/orgs', methods=['POST'])
@token_required
@admin_required
async def create_org():
    data = await request.get_json()
    db = next(get_db())

    existing = db.query(PlatformOrg).filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': '平台组织名称已存在'}), 400

    org = PlatformOrg(
        name=data['name'],
        description=data.get('description'),
        contact_name=data.get('contact_name'),
        contact_phone=data.get('contact_phone'),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return jsonify({'message': '平台组织创建成功', 'org': org.to_dict()}), 201


@platform_bp.route('/api/platform/orgs', methods=['GET'])
@token_required
@admin_required
async def list_orgs():
    db = next(get_db())
    orgs = db.query(PlatformOrg).order_by(PlatformOrg.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orgs])


@platform_bp.route('/api/platform/orgs/<int:org_id>', methods=['GET'])
@token_required
@admin_required
async def get_org(org_id: int):
    db = next(get_db())
    org = db.query(PlatformOrg).filter_by(id=org_id).first()
    if not org:
        return jsonify({'error': '平台组织不存在'}), 404

    groups = db.query(CommunityGroup).filter_by(platform_org_id=org_id).all()
    user_count = db.query(User).filter_by(platform_org_id=org_id).count()

    return jsonify({
        'org': org.to_dict(),
        'groups': [g.to_dict() for g in groups],
        'platform_user_count': user_count,
    })


@platform_bp.route('/api/platform/orgs/<int:org_id>', methods=['PUT'])
@token_required
@admin_required
async def update_org(org_id: int):
    data = await request.get_json()
    db = next(get_db())
    org = db.query(PlatformOrg).filter_by(id=org_id).first()
    if not org:
        return jsonify({'error': '平台组织不存在'}), 404

    for field in ['name', 'description', 'contact_name', 'contact_phone', 'status']:
        if field in data:
            setattr(org, field, data[field])
    db.commit()
    db.refresh(org)
    return jsonify({'message': '更新成功', 'org': org.to_dict()})


@platform_bp.route('/api/platform/orgs/<int:org_id>', methods=['DELETE'])
@token_required
@admin_required
async def suspend_org(org_id: int):
    db = next(get_db())
    org = db.query(PlatformOrg).filter_by(id=org_id).first()
    if not org:
        return jsonify({'error': '平台组织不存在'}), 404
    org.status = 'suspended'
    db.commit()
    return jsonify({'message': '平台组织已挂起'})


# ── 管理员：社区组 CRUD ──────────────────────────

@platform_bp.route('/api/platform/orgs/<int:org_id>/groups', methods=['POST'])
@token_required
@admin_required
async def create_group(org_id: int):
    db = next(get_db())
    org = db.query(PlatformOrg).filter_by(id=org_id).first()
    if not org:
        return jsonify({'error': '平台组织不存在'}), 404

    data = await request.get_json()
    group = CommunityGroup(
        platform_org_id=org_id,
        name=data['name'],
        description=data.get('description'),
        address=data.get('address'),
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return jsonify({'message': '社区组创建成功', 'group': group.to_dict()}), 201


@platform_bp.route('/api/platform/orgs/<int:org_id>/groups', methods=['GET'])
@token_required
@admin_required
async def list_groups(org_id: int):
    db = next(get_db())
    groups = db.query(CommunityGroup).filter_by(platform_org_id=org_id).order_by(CommunityGroup.created_at.desc()).all()
    return jsonify([g.to_dict() for g in groups])


@platform_bp.route('/api/platform/groups/<int:group_id>', methods=['PUT'])
@token_required
@admin_required
async def update_group(group_id: int):
    data = await request.get_json()
    db = next(get_db())
    group = db.query(CommunityGroup).filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': '社区组不存在'}), 404

    for field in ['name', 'description', 'address', 'status']:
        if field in data:
            setattr(group, field, data[field])
    db.commit()
    db.refresh(group)
    return jsonify({'message': '更新成功', 'group': group.to_dict()})


@platform_bp.route('/api/platform/groups/<int:group_id>', methods=['DELETE'])
@token_required
@admin_required
async def suspend_group(group_id: int):
    db = next(get_db())
    group = db.query(CommunityGroup).filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': '社区组不存在'}), 404
    group.status = 'suspended'
    db.commit()
    return jsonify({'message': '社区组已挂起'})


# ── 平台用户：组织信息与社区组 ──────────────────────────

@platform_bp.route('/api/platform/org', methods=['GET'])
@token_required
@role_required('platform')
async def get_my_org():
    user_id = request.current_user['user_id']
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if not user or not user.platform_org_id:
        return jsonify({'error': '未绑定平台组织'}), 400

    org = db.query(PlatformOrg).filter_by(id=user.platform_org_id).first()
    if not org:
        return jsonify({'error': '平台组织不存在'}), 404

    return jsonify({'org': org.to_dict()})


@platform_bp.route('/api/platform/communities', methods=['GET'])
@token_required
@role_required('platform')
async def list_my_communities():
    user_id = request.current_user['user_id']
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if not user or not user.platform_org_id:
        return jsonify({'error': '未绑定平台组织'}), 400

    groups = db.query(CommunityGroup).filter_by(
        platform_org_id=user.platform_org_id,
        status='active',
    ).all()

    result = []
    for g in groups:
        member_count = db.query(User).filter_by(community_group_id=g.id).count()
        d = g.to_dict()
        d['member_count'] = member_count
        result.append(d)

    return jsonify(result)


# ── 平台用户：聚合统计 ──────────────────────────

def _get_org_user_ids(db, platform_org_id: int):
    """获取平台组织下所有社区组的用户ID列表"""
    group_ids = [g.id for g in db.query(CommunityGroup).filter(
        CommunityGroup.platform_org_id == platform_org_id,
        CommunityGroup.status == 'active',
    ).all()]
    if not group_ids:
        return []
    return [u.id for u in db.query(User).filter(
        User.community_group_id.in_(group_ids),
    ).all()]


@platform_bp.route('/api/platform/stats', methods=['GET'])
@token_required
@role_required('platform')
async def platform_stats():
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.platform_org_id:
        return jsonify({'error': '未绑定平台组织'}), 400

    org_id = user.platform_org_id
    member_ids = _get_org_user_ids(db, org_id)

    now = datetime.now()
    start_date = now - timedelta(days=days)
    prev_start = start_date - timedelta(days=days)

    # 本期事件
    current_events = db.query(Event).filter(
        Event.created_at >= start_date,
        Event.user_id.in_(member_ids),
    ).all() if member_ids else []

    # 上期事件
    prev_events = db.query(Event).filter(
        Event.created_at >= prev_start,
        Event.created_at < start_date,
        Event.user_id.in_(member_ids),
    ).all() if member_ids else []

    # 统计
    stats = {'total': len(current_events), 'by_type': {}, 'by_risk': {}, 'by_status': {}}
    prev_stats = {'total': len(prev_events), 'by_type': {}, 'by_risk': {}, 'by_status': {}}

    for e in current_events:
        stats['by_type'][e.event_type] = stats['by_type'].get(e.event_type, 0) + 1
        stats['by_risk'][e.risk_level] = stats['by_risk'].get(e.risk_level, 0) + 1
        stats['by_status'][e.status] = stats['by_status'].get(e.status, 0) + 1

    for e in prev_events:
        prev_stats['by_type'][e.event_type] = prev_stats['by_type'].get(e.event_type, 0) + 1
        prev_stats['by_risk'][e.risk_level] = prev_stats['by_risk'].get(e.risk_level, 0) + 1
        prev_stats['by_status'][e.status] = prev_stats['by_status'].get(e.status, 0) + 1

    # 强制 DP
    budget_enabled = current_app.config.get('DP_BUDGET_ENABLED', True)
    epsilon = current_app.config.get('DP_DEFAULT_EPSILON', 0.8)

    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from dp_stats.stats_service import StatsService
    from dp_stats.budget_manager import BudgetManager
    from dp_stats.cache_service import DPResultCache

    bm = BudgetManager(daily_limit=3.0)
    cache = DPResultCache(ttl_minutes=10)
    svc = StatsService(budget_manager=bm, cache=cache)

    query_key = f"stats_{days}days"
    try:
        private_result = svc.get_private_stats(
            user_id=f"platform_{org_id}",
            query_key=query_key,
            stats={'total': stats['total'], 'by_type': stats['by_type'], 'by_risk': stats['by_risk'], 'by_status': stats['by_status']},
            epsilon=epsilon,
            now=now,
            check_budget=budget_enabled,
        )
        noisy = private_result['value']
        stats['total'] = noisy['total']
        stats['by_type'] = noisy['by_type']
        stats['by_risk'] = noisy['by_risk']
        stats['by_status'] = noisy['by_status']
        stats['display'] = private_result.get('display', {})
        stats['privacy_notice'] = f'统计结果已采用差分隐私技术处理（ε={epsilon}），数值与原始数据可能存在轻微差异'
    except ValueError as e:
        return jsonify({'error': '隐私预算已用完，请稍后再试', 'detail': str(e)}), 429

    # 趋势
    def calc_trend(cur, prev):
        return round((cur - prev) / prev * 100, 1) if prev else None

    stats['trends'] = {
        'total': calc_trend(stats['total'], prev_stats['total']),
        'by_type': {k: calc_trend(stats['by_type'].get(k, 0), prev_stats['by_type'].get(k, 0)) for k in stats['by_type']},
        'by_risk': {k: calc_trend(stats['by_risk'].get(k, 0), prev_stats['by_risk'].get(k, 0)) for k in stats['by_risk']},
    }
    stats['member_count'] = len(member_ids)
    stats['org_id'] = org_id
    return jsonify(stats)


@platform_bp.route('/api/platform/stats/daily', methods=['GET'])
@token_required
@role_required('platform')
async def platform_daily_trend():
    user_id = request.current_user['user_id']
    days = int(request.args.get('days', 7))

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.platform_org_id:
        return jsonify({'error': '未绑定平台组织'}), 400

    member_ids = _get_org_user_ids(db, user.platform_org_id)
    now = datetime.now()
    start_date = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

    events = db.query(Event).filter(
        Event.start_time >= start_date,
        Event.user_id.in_(member_ids),
    ).all() if member_ids else []

    event_types = ['FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL']
    dates = []
    daily_data = {}
    for i in range(days):
        date = (now - timedelta(days=days - 1 - i)).strftime('%m-%d')
        dates.append(date)
        daily_data[date] = {t: 0 for t in event_types}

    for e in events:
        date_key = e.start_time.strftime('%m-%d')
        if date_key in daily_data and e.event_type in event_types:
            daily_data[date_key][e.event_type] += 1

    return jsonify({
        'dates': dates,
        'by_type': {t: [daily_data[d][t] for d in dates] for t in event_types},
    })


# ── 普通用户：社区组选择 ──────────────────────────

@platform_bp.route('/api/community/groups', methods=['GET'])
@token_required
@role_required('user', 'admin')
async def available_groups():
    """获取可选社区组列表"""
    db = next(get_db())
    search = request.args.get('search', '').strip()

    query = db.query(CommunityGroup).filter_by(status='active')
    if search:
        query = query.filter(CommunityGroup.name.contains(search))

    groups = query.order_by(CommunityGroup.name).all()

    result = []
    for g in groups:
        org = db.query(PlatformOrg).filter_by(id=g.platform_org_id).first()
        member_count = db.query(User).filter_by(community_group_id=g.id).count()
        d = g.to_dict()
        d['org_name'] = org.name if org else ''
        d['member_count'] = member_count
        result.append(d)

    return jsonify(result)


@platform_bp.route('/api/user/community', methods=['GET'])
@token_required
@role_required('user', 'admin')
async def get_user_community():
    user_id = request.current_user['user_id']
    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if not user or not user.community_group_id:
        return jsonify({'community': None})

    group = db.query(CommunityGroup).filter_by(id=user.community_group_id).first()
    if not group:
        return jsonify({'community': None})

    org = db.query(PlatformOrg).filter_by(id=group.platform_org_id).first()
    d = group.to_dict()
    d['org_name'] = org.name if org else ''
    return jsonify({'community': d})


@platform_bp.route('/api/user/community', methods=['PUT'])
@token_required
@role_required('user', 'admin')
async def set_user_community():
    user_id = request.current_user['user_id']
    data = await request.get_json()
    group_id = data.get('community_group_id')

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()

    if group_id is None:
        # 取消绑定
        user.community_group_id = None
        db.commit()
        return jsonify({'message': '已取消社区组绑定', 'community': None})

    group = db.query(CommunityGroup).filter_by(id=group_id, status='active').first()
    if not group:
        return jsonify({'error': '社区组不存在或已停用'}), 404

    user.community_group_id = group_id
    db.commit()
    return jsonify({'message': '社区组已更新', 'community': group.to_dict()})

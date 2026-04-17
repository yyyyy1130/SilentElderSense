from quart import Blueprint, request, jsonify
from .models import User, get_db
from .utils import generate_token, token_required, admin_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/register', methods=['POST'])
async def register():
    """注册接口"""
    data = await request.get_json()

    db = next(get_db())

    existing_user = db.query(User).filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': '用户名已存在'}), 400

    user = User(
        username=data['username'],
        email=data.get('email'),
        role='user'
    )
    user.set_password(data['password'])

    db.add(user)
    db.commit()

    return jsonify({'message': '注册成功'}), 201


@auth_bp.route('/api/login', methods=['POST'])
async def login():
    """登录接口"""
    data = await request.get_json()

    db = next(get_db())

    user = db.query(User).filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        token = generate_token(user.id, user.username, user.role)
        result = {
            'message': '登录成功',
            'access_token': token,
            'token_type': 'Bearer',
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'community_group_id': user.community_group_id,
        }
        if user.role == 'platform':
            result['org_name'] = user.org_name
            result['org_description'] = user.org_description
        return jsonify(result), 200
    else:
        return jsonify({'error': '用户名或密码错误'}), 401


@auth_bp.route('/api/protected', methods=['GET'])
@token_required
async def protected_route():
    """受保护的路由示例"""
    user = request.current_user
    return jsonify({
        'message': '这是一个受保护的路由',
        'user_id': user['user_id'],
        'username': user['username'],
        'role': user.get('role', 'user')
    }), 200


@auth_bp.route('/api/users/platform', methods=['POST'])
@token_required
@admin_required
async def create_platform_user():
    """管理员创建平台用户"""
    data = await request.get_json()
    db = next(get_db())

    existing = db.query(User).filter_by(username=data['username']).first()
    if existing:
        return jsonify({'error': '用户名已存在'}), 400

    user = User(
        username=data['username'],
        email=data.get('email'),
        role='platform',
        org_name=data.get('org_name'),
        org_description=data.get('org_description'),
        org_contact_name=data.get('org_contact_name'),
        org_contact_phone=data.get('org_contact_phone'),
    )
    user.set_password(data['password'])

    db.add(user)
    db.commit()

    return jsonify({'message': '平台用户创建成功', 'username': user.username, 'role': user.role}), 201


@auth_bp.route('/api/users', methods=['GET'])
@token_required
@admin_required
async def list_users():
    """管理员获取用户列表"""
    db = next(get_db())
    users = db.query(User).order_by(User.created_at.desc()).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'org_name': u.org_name,
        'org_contact_name': u.org_contact_name,
        'org_contact_phone': u.org_contact_phone,
        'community_group_id': u.community_group_id,
        'created_at': u.created_at.isoformat() if u.created_at else None,
    } for u in users])


@auth_bp.route('/api/admin/reset-password', methods=['POST'])
@token_required
@admin_required
async def reset_password():
    """管理员重设用户密码"""
    data = await request.get_json()
    user_id = data.get('user_id')
    new_password = data.get('new_password')

    if not user_id or not new_password:
        return jsonify({'error': '缺少 user_id 或 new_password'}), 400

    if len(new_password) < 4:
        return jsonify({'error': '密码长度至少4位'}), 400

    db = next(get_db())
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    user.set_password(new_password)
    db.commit()
    return jsonify({'message': f'用户 {user.username} 密码已重置'})

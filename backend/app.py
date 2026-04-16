from quart import Quart, request, jsonify
from config import Config, DevelopmentConfig, ProductionConfig
from auth import init_db, auth_bp
from detect import detect_bp
from events import events_bp
from alerts import alerts_bp
from datetime import datetime
import psutil
import os
import argparse

# 在模块加载时解析参数（影响配置选择）
parser = argparse.ArgumentParser(description='Silent Elder Sense Backend')
parser.add_argument('--prod', action='store_true', help='生产模式（启用差分隐私）')
parser.add_argument('--port', type=int, default=8000, help='端口')
_args, _remaining = parser.parse_known_args()

app = Quart(__name__)

# 根据参数选择配置
if _args.prod:
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# 允许上传大文件（最大 500MB）
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# 初始化数据库
init_db(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(detect_bp)
app.register_blueprint(events_bp)
app.register_blueprint(alerts_bp)

# CORS 中间件（支持预检请求和携带认证的请求）
@app.after_request
async def after_request(response):
    origin = request.headers.get('Origin')
    # 允许的来源
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 处理 OPTIONS 预检请求
@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
async def handle_options(path=''):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        return '', 204, {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
        }
    return '', 204

@app.route('/')
async def index():
    return {
        'message': 'Backend API is running',
        'dp_budget_enabled': app.config.get('DP_BUDGET_ENABLED', True)
    }


@app.route('/api/system/status', methods=['GET'])
async def system_status():
    """
    系统状态 API

    返回各服务的运行状态
    """
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    services = [
        {
            'name': '识别引擎',
            'desc': 'AI行为识别服务',
            'status': 'online',
            'statusText': '运行中'
        },
        {
            'name': '数据采集',
            'desc': '视频流采集服务',
            'status': 'online',
            'statusText': '运行中'
        }
    ]

    return jsonify({
        'services': services,
        'resources': {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / (1024**3), 1),
            'memory_total_gb': round(memory.total / (1024**3), 1)
        },
        'uptime': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # 配置已在模块顶部根据参数加载
    dp_status = "启用" if _args.prod else "禁用"
    print(f"启动模式：{'生产' if _args.prod else '开发'}（差分隐私 {dp_status}）")
    app.run(debug=not _args.prod, port=_args.port)

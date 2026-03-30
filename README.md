# 面向独居老人的隐私保护型异常行为识别与应急响应系统

## 快速启动

### 后端

进入后端目录：

```bash
cd backend
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动后端：

```bash
python app.py
```

后端运行在 http://localhost:8000

### 前端

进入前端目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

启动前端：

```bash
npm run dev
```

前端运行在 http://localhost:3000

## 说明

- 数据库使用 SQLite，无需额外安装数据库服务
- 首次启动后端会自动创建数据库文件 `backend/data/db.sqlite3`

## 模拟数据生成（可选）

首次启动后，可生成测试数据用于演示。

进入后端目录：

```bash
cd backend
```

运行生成脚本：

```bash
python tools/generate_mock_data.py
```

生成内容：

- 用户：`admin` / `test`（密码均为 `123456`）
- 事件：100-200 条随机事件（过去7天）
# 校园 AI 秘书 - 完整版

基于 Qwen 大模型的校园日程管理和智能问答服务，包含 Web 管理后台。

## 功能特性

### ✅ 已完成

#### Phase 1: 智能信息解析
- 自然语言解析：识别时间、地点、事件等实体
- 支持相对时间表达（如"明天下午 3 点"、"下周一"）
- 优先级自动推断
- 置信度评估

#### Phase 2: RAG 知识库 + 智能问答
- 基于向量数据库的语义检索
- 校园知识库管理
- 智能问答服务
- 知识库来源追溯

#### Phase 5: 主动提醒系统
- 多级提醒（提前 1 天、3 小时等）
- 定时扫描检查
- 避免重复提醒
- 异步任务调度

#### 🆕 管理后台
- 用户认证系统（JWT）
- MySQL 数据库支持
- 可视化仪表盘
- 用户管理
- 日程管理
- 知识库管理
- 提醒日志查看
- 系统信息

---

## 技术栈

| 模块 | 技术选型 |
|------|---------|
| 后端框架 | FastAPI |
| 前端框架 | Vue 3 + Element Plus |
| 图表 | ECharts |
| LLM | Qwen (阿里云 DashScope) |
| 向量数据库 | Qdrant (内存模式) |
| 关系数据库 | MySQL / SQLite |
| 缓存 | Redis (可选) |
| 日志 | Loguru |

---

## 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 5.7+ (或使用 SQLite)
- Windows / Linux / macOS

### 2. 一键安装（Windows）

```cmd
cd campus_ai_secretary
scripts\setup.bat
```

### 3. 手动安装

```bash
# 进入项目目录
cd campus_ai_secretary

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

**必填配置**：

```env
# 千问 API Key（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# MySQL 数据库（可选，默认使用 SQLite）
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/campus_ai?charset=utf8mb4
```

### 5. 初始化数据库

```bash
# Windows
scripts\init_db.bat

# Linux/macOS
python scripts/init_db.py
```

### 6. 启动服务

```bash
# Windows
scripts\run_demo.bat

# Linux/macOS
bash scripts/run_demo.sh

# 或直接运行
python -m app.main
```

### 7. 访问服务

| 服务 | 地址 |
|------|------|
| API 文档 | http://localhost:8000/docs |
| 管理后台 | http://localhost:8000/admin |
| 健康检查 | http://localhost:8000/health |

**默认管理员账号**：
- 用户名：`admin`
- 密码：`admin123`

---

## 管理后台功能

### 仪表盘
- 用户统计（总数、活跃数）
- 日程统计（总数、待处理、已完成、今日）
- 提醒统计（总数、今日）
- 知识库统计
- 用户增长趋势图
- 日程统计图

### 用户管理
- 用户列表查看
- 搜索用户（用户名/邮箱/昵称）
- 启用/禁用用户
- 查看用户日程数

### 日程管理
- 所有用户日程列表
- 按状态/优先级筛选
- 删除日程
- 分页浏览

### 知识库管理
- 知识库文档列表
- 添加新文档
- 查看文档内容
- 删除文档
- 按状态筛选

### 提醒日志
- 提醒发送记录
- 查看提醒状态
- 分页浏览

### 系统设置
- 系统版本信息
- Python 版本
- 运行平台
- 数据库类型

---

## API 接口

### 认证接口
| 接口 | 方法 | 路径 |
|------|------|------|
| 登录 | POST | `/api/v1/auth/login` |
| 获取当前用户 | GET | `/api/v1/auth/me` |
| 用户注册 | POST | `/api/v1/auth/register` |

### 管理接口（需要管理员权限）
| 接口 | 方法 | 路径 |
|------|------|------|
| 仪表盘统计 | GET | `/api/admin/dashboard/stats` |
| 用户增长图表 | GET | `/api/admin/dashboard/chart/users` |
| 日程图表 | GET | `/api/admin/dashboard/chart/schedules` |
| 用户列表 | GET | `/api/admin/users` |
| 切换用户状态 | PUT | `/api/admin/users/{id}/toggle` |
| 日程列表 | GET | `/api/admin/schedules` |
| 删除日程 | DELETE | `/api/admin/schedules/{id}` |
| 知识库列表 | GET | `/api/admin/knowledge` |
| 添加知识库 | POST | `/api/admin/knowledge` |
| 删除知识库 | DELETE | `/api/admin/knowledge/{id}` |
| 提醒日志 | GET | `/api/admin/reminders` |
| 系统信息 | GET | `/api/admin/system/info` |

---

## 项目结构

```
campus_ai_secretary/
├── admin/                      # 管理后台前端
│   └── index.html
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── schedule.py    # 日程 API
│   │   │   ├── parse.py       # 解析 API
│   │   │   ├── qa.py          # 问答 API
│   │   │   └── auth.py        # 认证 API
│   │   └── admin.py           # 管理后台 API
│   ├── core/
│   │   ├── llm.py            # Qwen LLM
│   │   ├── rag.py            # RAG 引擎
│   │   ├── parser.py         # 解析器
│   │   ├── scheduler.py      # 日程管理
│   │   ├── reminder.py       # 提醒服务
│   │   └── auth.py           # 认证模块
│   ├── database/
│   │   ├── connection.py     # 数据库连接
│   │   └── models.py         # 数据模型
│   ├── models/
│   │   └── schedule.py       # 日程模型
│   ├── utils/
│   │   ├── time_utils.py     # 时间工具
│   │   └── logger.py         # 日志工具
│   └── main.py               # 服务入口
├── data/
│   └── knowledge_base/
├── scripts/
│   ├── setup.bat            # 安装脚本
│   ├── init_db.py           # 数据库初始化
│   ├── init_db.bat          # Windows 初始化
│   ├── run_demo.bat         # Windows 启动
│   ├── run_demo.sh          # Linux 启动
│   ├── test_api.py          # API 测试
│   └── qqbot_adapter.py     # QQbot 适配
├── .env                      # 环境变量
├── .env.example              # 环境变量示例
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

---

## 数据库模型

### users - 用户表
- id, username, password_hash, email, nickname, avatar, role, is_active, created_at, last_login

### schedules - 日程表
- id, user_id, event_name, start_time, end_time, location, source, priority, description, remind_times, status, created_at

### knowledge_base - 知识库表
- id, title, content, source_type, source_url, category, tags, priority, valid_from, valid_to, is_active, view_count, created_at

### reminder_logs - 提醒日志表
- id, user_id, schedule_id, remind_time, event_time, event_name, offset, status, message, sent_at

### system_stats - 系统统计表
- id, stat_date, total_users, active_users, total_schedules, completed_schedules, total_reminders, api_calls, created_at

---

## 常见问题

### Q: 如何切换 Qwen 模型？
A: 在 `app/core/llm.py` 中修改 `model` 参数，可选值：`qwen-plus`, `qwen-max`, `qwen-turbo`

### Q: 不使用 MySQL 可以吗？
A: 可以，系统会自动降级使用 SQLite（无需配置）

### Q: 忘记管理员密码怎么办？
A: 直接修改数据库 users 表，或删除数据库文件重新初始化

### Q: 管理后台打不开？
A: 检查是否正确挂载了 `/admin` 静态文件目录，确保 `admin/index.html` 存在

---

## 开发计划

### 已完成 ✅
- [x] Phase 1: 智能信息解析
- [x] Phase 2: RAG 知识库 + 智能问答
- [x] Phase 5: 主动提醒系统
- [x] 管理后台（用户/日程/知识库）
- [x] MySQL 数据库支持
- [x] JWT 认证系统

### 待实现
- [ ] Phase 3: 图片 OCR 识别（课表截图）
- [ ] Phase 4: QQ 机器人完整接入
- [ ] Web 管理界面增强（日程可视化编辑）
- [ ] 数据导出功能
- [ ] 多租户支持
- [ ] 与教务系统对接

---

## License

MIT License

---

**开发完成** ✅  
**管理后台**: http://localhost:8000/admin

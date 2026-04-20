# 校园 AI 秘书 Demo 完成报告

**完成日期**: 2024 年 4 月 20 日  
**版本**: v1.0.0  
**技术栈**: Python 3.10+ / FastAPI / Qwen / Qdrant

---

## 一、已完成功能

### ✅ Phase 1: 智能信息解析

| 功能 | 状态 | 说明 |
|------|------|------|
| 自然语言时间解析 | ✅ | 支持"明天下午 3 点"、"下周一"等表达 |
| 地点实体识别 | ✅ | 识别教学楼、图书馆等校园地点 |
| 事件名称提取 | ✅ | 基于关键词和 LLM 提取 |
| 优先级推断 | ✅ | 根据事件类型自动判断优先级 |
| 置信度评估 | ✅ | 评估解析结果可靠性 |

**核心文件**:
- `app/core/parser.py` - 实体解析器
- `app/utils/time_utils.py` - 时间解析工具
- `app/api/v1/parse.py` - 解析 API

---

### ✅ Phase 2: RAG 知识库 + 智能问答

| 功能 | 状态 | 说明 |
|------|------|------|
| 向量数据库 | ✅ | Qdrant 内存模式（Demo） |
| 文档添加 | ✅ | 支持单篇/批量添加 |
| 语义检索 | ✅ | 基于向量相似度检索 |
| 智能问答 | ✅ | 基于 Qwen 生成回答 |
| 来源追溯 | ✅ | 显示知识库来源 |

**核心文件**:
- `app/core/rag.py` - RAG 检索引擎
- `app/core/llm.py` - Qwen LLM 封装
- `app/api/v1/qa.py` - 问答 API

---

### ✅ Phase 5: 主动提醒系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 定时扫描 | ✅ | 可配置检查间隔 |
| 多级提醒 | ✅ | 支持提前 1 天、3 小时等 |
| 避免重复 | ✅ | 记录已发送提醒 |
| 异步任务 | ✅ | asyncio 后台运行 |
| 回调通知 | ✅ | 支持自定义发送回调 |

**核心文件**:
- `app/core/reminder.py` - 提醒服务
- `app/core/scheduler.py` - 日程管理器
- `app/main.py` - 服务入口（含提醒启动）

---

## 二、项目结构

```
campus_ai_secretary/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── schedule.py      # 日程管理 API
│   │       ├── parse.py         # 信息解析 API
│   │       └── qa.py            # 智能问答 API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm.py              # Qwen LLM 封装
│   │   ├── rag.py              # RAG 检索引擎
│   │   ├── parser.py           # 信息解析器
│   │   ├── scheduler.py        # 日程管理器
│   │   └── reminder.py         # 提醒服务
│   ├── models/
│   │   ├── __init__.py
│   │   └── schedule.py         # 数据模型
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── time_utils.py       # 时间解析工具
│   │   └── logger.py           # 日志工具
│   └── main.py                 # 服务入口
├── data/
│   └── knowledge_base/         # 知识库数据目录
├── scripts/
│   ├── __init__.py
│   ├── test_api.py            # API 测试脚本
│   ├── qqbot_adapter.py       # QQbot 适配器
│   ├── run_demo.bat           # Windows 启动脚本
│   └── run_demo.sh            # Linux/macOS启动脚本
├── .env                        # 环境变量配置
├── .env.example                # 环境变量示例
├── requirements.txt            # 依赖列表
└── README.md                   # 项目说明
```

---

## 三、API 接口清单

### 日程管理
| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 创建日程 | POST | `/api/v1/schedule/create` | 创建新日程 |
| 获取日程 | GET | `/api/v1/schedule/{id}` | 获取详情 |
| 日程列表 | GET | `/api/v1/schedule/list` | 获取列表 |
| 更新日程 | PUT | `/api/v1/schedule/{id}` | 更新日程 |
| 删除日程 | DELETE | `/api/v1/schedule/{id}` | 删除日程 |
| 检查冲突 | GET | `/api/v1/schedule/{id}/conflict` | 检查冲突 |
| 统计信息 | GET | `/api/v1/schedule/stats` | 获取统计 |
| 即将到来的 | GET | `/api/v1/schedule/upcoming` | 即将到期 |

### 信息解析
| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 解析文本 | POST | `/api/v1/parse/text` | 解析文本 |
| 解析转发 | POST | `/api/v1/parse/forwarded` | 解析转发消息 |
| 确认消息 | POST | `/api/v1/parse/confirm-message` | 生成确认消息 |

### 智能问答
| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 智能问答 | POST | `/api/v1/qa/ask` | 基于知识库问答 |
| 添加文档 | POST | `/api/v1/qa/kb/add` | 添加知识库文档 |
| 批量添加 | POST | `/api/v1/qa/kb/batch-add` | 批量添加文档 |
| 知识库统计 | GET | `/api/v1/qa/kb/stats` | 获取统计 |

---

## 四、快速开始

### 1. 安装依赖

```bash
cd campus_ai_secretary
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 DASHSCOPE_API_KEY
```

### 3. 获取 DashScope API Key

访问：https://dashscope.console.aliyun.com/

### 4. 启动服务

```bash
# Windows
scripts\run_demo.bat

# Linux/macOS
bash scripts/run_demo.sh

# 或直接运行
python -m app.main
```

### 5. 访问服务

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 6. 测试 API

```bash
python scripts/test_api.py
```

---

## 五、QQbot 集成说明

### 适配器使用

`scripts/qqbot_adapter.py` 提供了 QQbot 集成适配器：

```python
from scripts.qqbot_adapter import on_qq_message

# 在 QQbot 插件中调用
async def handle_message(user_id, content):
    reply = await on_qq_message(user_id, content)
    return reply
```

### 与 OpenClaw QQbot 集成

由于 OpenClaw 已有 QQbot 插件，可以通过以下方式集成：

1. **方式一**: 在 OpenClaw 中配置 webhook 转发到校园 AI 秘书服务
2. **方式二**: 修改 qqbot_adapter.py 作为 OpenClaw 的子模块调用
3. **方式三**: 使用 sessions_spawn 在 OpenClaw 内调用 API

---

## 六、待实现功能

### Phase 3: 图片 OCR 识别
- [ ] 接入 PaddleOCR
- [ ] 课表截图解析
- [ ] 通知截图解析

### Phase 4: QQ 机器人接入
- [ ] NoneBot2 完整实现
- [ ] 群消息监听
- [ ] 私聊消息处理

### 增强功能
- [ ] 用户认证系统
- [ ] 数据持久化 (SQLite/PostgreSQL)
- [ ] Web 管理界面
- [ ] 多用户支持
- [ ] 日程共享功能
- [ ] 与教务系统对接

---

## 七、技术说明

### Qwen 模型选择

当前使用 `qwen-plus`，可切换：
- `qwen-turbo` - 快速、低成本
- `qwen-plus` - 平衡性能与成本（推荐）
- `qwen-max` - 最强性能

修改位置：`app/core/llm.py` 第 25 行

### Qdrant 模式

- **内存模式**: `QDRANT_MODE=memory` (Demo 默认)
- **服务模式**: 需部署 Qdrant 服务

生产环境部署：
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

### 提醒服务

提醒检查间隔可在 `.env` 中配置：
```env
REMINDER_CHECK_INTERVAL=60  # 60 秒检查一次
```

---

## 八、注意事项

1. **API Key 安全**: 不要将 `.env` 提交到版本控制
2. **内存模式**: Demo 使用内存存储，重启后数据丢失
3. **生产部署**: 需要配置 Redis 和 Qdrant 服务
4. **速率限制**: DashScope API 有调用限制

---

## 九、测试账号

Demo 内置测试数据：
- 用户 ID: `demo_user`
- 示例日程：高等数学期末考试、实验报告提交等
- 知识库：图书馆、教务处、校医院信息

---

**开发完成** ✅  
**下一步**: 根据用户反馈迭代优化

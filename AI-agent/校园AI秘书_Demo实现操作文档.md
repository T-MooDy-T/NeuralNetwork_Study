# 校园AI秘书 Demo 实现操作文档

**文档版本**：V1.0  
**适用环境**：Windows/Linux/macOS  
**技术栈**：Python 3.10 + FastAPI + Redis + Qdrant  

---

## 一、项目概述

本文档详细描述如何实现一个校园AI秘书的最小可行版本（MVP），包含以下核心功能：

1. **智能信息解析**：支持文字、图片、转发消息的解析
2. **RAG知识库检索**：基于向量数据库的语义检索
3. **日程管理**：结构化日程的创建、查询、提醒
4. **QQ机器人交互**：通过QQ频道/私聊与用户交互

---

## 二、技术选型

| 模块 | 技术方案 | 版本 | 选型理由 |
|-----|---------|------|---------|
| 后端框架 | FastAPI | 0.104.1 | 高性能、自动API文档、异步支持 |
| 向量数据库 | Qdrant | 1.7.0 | 轻量级、支持中文语义检索、部署简单 |
| 缓存 | Redis | 7.2 | 会话管理、热点数据缓存 |
| 嵌入模型 | text-embedding-3-small | OpenAI API | 支持中英文、向量维度适中 |
| 大语言模型 | gpt-4o-mini | OpenAI API | 成本低、响应快、支持结构化输出 |
| OCR识别 | PaddleOCR | 2.7.0 | 开源免费、中文识别效果好 |
| QQ机器人 | NoneBot2 | 2.2.0 | 成熟的QQ机器人框架 |

---

## 三、环境搭建

### 3.1 前置依赖安装

#### 3.1.1 安装 Python 环境

```bash
# 检查Python版本
python --version  # 需要 3.10+

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

#### 3.1.2 安装核心依赖

```bash
pip install fastapi uvicorn qdrant-client redis openai paddlepaddle paddleocr nonebot2 nonebot-adapter-onebot

# 安装其他依赖
pip install python-dotenv pydantic requests beautifulsoup4 numpy
```

### 3.2 启动服务

#### 3.2.1 启动 Redis（用于缓存和会话管理）

```bash
# Windows（使用WSL或Docker）
docker run -d -p 6379:6379 redis:7.2

# Linux（直接安装）
sudo apt-get install redis-server
sudo systemctl start redis
```

#### 3.2.2 启动 Qdrant 向量数据库

```bash
# 使用Docker启动
docker run -d -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# 验证服务
curl http://localhost:6333/health
# 预期输出: {"status":"ok"}
```

#### 3.2.3 配置环境变量

创建 `.env` 文件：

```env
# OpenAI API配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Qdrant配置
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=campus_ai

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 服务配置
APP_PORT=8000
DEBUG=true
```

---

## 四、核心代码实现

### 4.1 项目结构

```
campus_ai_secretary/
├── app/
│   ├── api/                    # REST API接口
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── schedule.py     # 日程管理接口
│   │   │   ├── parse.py        # 信息解析接口
│   │   │   └── qa.py           # 智能问答接口
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── rag.py              # RAG检索引擎
│   │   ├── parser.py           # 信息解析器
│   │   ├── scheduler.py        # 日程管理器
│   │   └── ocr.py              # OCR识别模块
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── schedule.py         # 日程数据模型
│   │   ├── query.py            # 查询请求模型
│   │   └── response.py         # 响应模型
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── time_utils.py       # 时间解析工具
│   │   └── logger.py           # 日志工具
│   └── main.py                 # 服务入口
├── data/                       # 数据目录
│   ├── knowledge_base/         # 知识库原始数据
│   └── init_data.py            # 初始化脚本
├── bot/                        # QQ机器人
│   ├── __init__.py
│   └── campus_bot.py           # NoneBot2机器人实现
├── .env                        # 环境变量配置
└── requirements.txt            # 依赖列表
```

### 4.2 数据模型定义

#### 4.2.1 日程数据模型 (`app/models/schedule.py`)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ScheduleItem(BaseModel):
    id: str = Field(description="日程唯一标识")
    event_name: str = Field(description="事件名称")
    start_time: datetime = Field(description="开始时间")
    end_time: datetime = Field(description="结束时间")
    location: Optional[str] = Field(None, description="地点")
    source: str = Field(description="信息来源")
    priority: str = Field("medium", description="优先级: high/medium/low")
    description: Optional[str] = Field(None, description="详细描述")
    remind_times: List[str] = Field(default_factory=list, description="提醒时间点")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class ScheduleCreate(BaseModel):
    event_name: str = Field(description="事件名称")
    start_time: str = Field(description="开始时间（支持自然语言）")
    end_time: Optional[str] = Field(None, description="结束时间")
    location: Optional[str] = Field(None, description="地点")
    source: Optional[str] = Field("user", description="信息来源")
    priority: Optional[str] = Field("medium", description="优先级")
    description: Optional[str] = Field(None, description="详细描述")
```

#### 4.2.2 查询请求模型 (`app/models/query.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional

class ParseRequest(BaseModel):
    content: str = Field(description="待解析内容（文字或图片URL）")
    content_type: str = Field("text", description="内容类型: text/image/forward")
    user_id: str = Field(description="用户ID")

class QueryRequest(BaseModel):
    question: str = Field(description="用户问题")
    user_id: str = Field(description="用户ID")
    context: Optional[str] = Field(None, description="上下文信息")
```

### 4.3 RAG检索引擎实现

#### 4.3.1 向量数据库初始化 (`app/core/rag.py`)

```python
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), 
                           base_url=os.getenv("OPENAI_BASE_URL"))
        self.qdrant = QdrantClient(
            host=os.getenv("QDRANT_HOST"),
            port=int(os.getenv("QDRANT_PORT"))
        )
        self.collection_name = os.getenv("QDRANT_COLLECTION", "campus_ai")
        self._init_collection()

    def _init_collection(self):
        """初始化向量数据库集合"""
        collections = self.qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )
            print(f"Collection {self.collection_name} created successfully")

    def get_embedding(self, text: str) -> list:
        """获取文本嵌入向量"""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def add_document(self, content: str, metadata: dict):
        """添加文档到知识库"""
        embedding = self.get_embedding(content)
        point = PointStruct(
            id=metadata.get("chunk_id"),
            vector=embedding,
            payload={
                "content": content,
                **metadata
            }
        )
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def search(self, query: str, top_k: int = 5) -> list:
        """检索相关文档"""
        query_embedding = self.get_embedding(query)
        results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )
        
        return [
            {
                "content": result.payload.get("content"),
                "metadata": {k: v for k, v in result.payload.items() if k != "content"},
                "score": result.score
            }
            for result in results
        ]
```

### 4.4 信息解析器实现

#### 4.4.1 时间解析工具 (`app/utils/time_utils.py`)

```python
import re
from datetime import datetime, timedelta

def parse_time(time_str: str) -> datetime:
    """解析自然语言时间为标准datetime对象"""
    time_str = time_str.strip()
    
    # 相对时间解析
    relative_patterns = [
        (r"今天", timedelta(days=0)),
        (r"明天", timedelta(days=1)),
        (r"后天", timedelta(days=2)),
        (r"昨天", timedelta(days=-1)),
        (r"本周", timedelta(days=0)),
        (r"下周", timedelta(weeks=1)),
    ]
    
    for pattern, delta in relative_patterns:
        if pattern in time_str:
            base_date = datetime.now().replace(hour=0, minute=0, second=0)
            time_str = time_str.replace(pattern, "")
            base_date += delta
            break
    else:
        base_date = datetime.now()
    
    # 日期解析
    date_patterns = [
        r"(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})[日号]?",
        r"(\d{1,2})[月/-](\d{1,2})[日号]?",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, time_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                year, month, day = map(int, groups)
            else:
                year = base_date.year
                month, day = map(int, groups)
            base_date = datetime(year, month, day)
            time_str = re.sub(pattern, "", time_str)
            break
    
    # 时间解析
    time_pattern = r"(\d{1,2}):(\d{2})(?::(\d{2}))?"
    match = re.search(time_pattern, time_str)
    if match:
        groups = match.groups()
        hour = int(groups[0])
        minute = int(groups[1])
        second = int(groups[2]) if groups[2] else 0
    else:
        hour, minute, second = 0, 0, 0
    
    return datetime(base_date.year, base_date.month, base_date.day, hour, minute, second)
```

#### 4.4.2 实体解析器 (`app/core/parser.py`)

```python
import re
from datetime import datetime
from typing import Dict, Optional, Tuple
from .ocr import OCREngine
from ..utils.time_utils import parse_time

class EntityParser:
    def __init__(self):
        self.ocr_engine = OCREngine()
        
    def parse_text(self, content: str) -> Dict:
        """解析文本内容，提取实体信息"""
        result = {
            "event_name": None,
            "start_time": None,
            "end_time": None,
            "location": None,
            "priority": "medium",
            "description": content
        }
        
        # 提取地点
        location_patterns = [
            r"(教学楼|实验楼|图书馆|体育馆|食堂|报告厅|会议室)[A-Z]?\d+",
            r"(教室|房间|室)\s*([A-Z]?\d+)",
            r"(校区)\s*([\u4e00-\u9fa5]+)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content)
            if match:
                result["location"] = match.group()
                break
        
        # 提取时间范围
        time_pattern = r"(\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日号]?\s*\d{1,2}:\d{2})\s*[到至-]\s*(\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日号]?\s*\d{1,2}:\d{2})?"
        match = re.search(time_pattern, content)
        if match:
            result["start_time"] = parse_time(match.group(1))
            if match.group(2):
                result["end_time"] = parse_time(match.group(2))
        
        # 如果没有完整时间范围，尝试提取单个时间
        if not result["start_time"]:
            time_patterns = [
                r"\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日号]?\s*\d{1,2}:\d{2}",
                r"(今天|明天|后天)\s*\d{1,2}:\d{2}",
                r"下(周一|周二|周三|周四|周五|周六|周日)\s*\d{1,2}:\d{2}",
            ]
            for pattern in time_patterns:
                match = re.search(pattern, content)
                if match:
                    result["start_time"] = parse_time(match.group())
                    # 默认持续1小时
                    result["end_time"] = result["start_time"] + timedelta(hours=1)
                    break
        
        # 提取事件名称（基于关键词）
        event_keywords = {
            "考试": ["考试", "期末", "期中", "测验"],
            "作业": ["作业", "报告", "论文", "实验"],
            "会议": ["会议", "例会", "讨论", "答辩"],
            "活动": ["活动", "比赛", "讲座", "演出"],
            "课程": ["上课", "课程", "课", "讲座"],
        }
        
        event_name = ""
        for event_type, keywords in event_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    event_name = f"{event_type}"
                    # 尝试提取更具体的名称
                    course_match = re.search(r"([\u4e00-\u9fa5]+(?:课程|课))", content)
                    if course_match:
                        event_name = course_match.group(1)
                    result["event_name"] = event_name
                    result["priority"] = "high" if event_type in ["考试", "作业"] else "medium"
                    break
            if event_name:
                break
        
        if not result["event_name"]:
            result["event_name"] = "待命名事件"
        
        return result
    
    def parse_image(self, image_path: str) -> Dict:
        """解析图片内容（课表截图等）"""
        text = self.ocr_engine.extract_text(image_path)
        return self.parse_text(text)
```

### 4.5 日程管理器实现

#### 4.5.1 日程CRUD操作 (`app/core/scheduler.py`)

```python
import uuid
import redis
import json
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.schedule import ScheduleItem, ScheduleCreate
from ..utils.time_utils import parse_time

class ScheduleManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=int(os.getenv("REDIS_DB"))
        )
    
    def create_schedule(self, user_id: str, data: ScheduleCreate) -> ScheduleItem:
        """创建日程"""
        schedule_id = str(uuid.uuid4())
        
        start_time = parse_time(data.start_time)
        end_time = parse_time(data.end_time) if data.end_time else start_time + timedelta(hours=1)
        
        schedule = ScheduleItem(
            id=schedule_id,
            event_name=data.event_name,
            start_time=start_time,
            end_time=end_time,
            location=data.location,
            source=data.source or "user",
            priority=data.priority or "medium",
            description=data.description,
            remind_times=["提前1天", "当天"]
        )
        
        # 存储到Redis
        key = f"schedule:{user_id}:{schedule_id}"
        self.redis.set(key, schedule.model_dump_json())
        
        # 更新用户日程列表
        user_key = f"user:{user_id}:schedules"
        self.redis.sadd(user_key, schedule_id)
        
        return schedule
    
    def get_schedule(self, user_id: str, schedule_id: str) -> Optional[ScheduleItem]:
        """获取单个日程"""
        key = f"schedule:{user_id}:{schedule_id}"
        data = self.redis.get(key)
        if data:
            return ScheduleItem.model_validate_json(data)
        return None
    
    def list_schedules(self, user_id: str, start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None) -> List[ScheduleItem]:
        """获取用户日程列表"""
        user_key = f"user:{user_id}:schedules"
        schedule_ids = self.redis.smembers(user_key)
        
        schedules = []
        for schedule_id in schedule_ids:
            schedule = self.get_schedule(user_id, schedule_id.decode())
            if schedule:
                # 日期过滤
                if start_date and schedule.start_time < start_date:
                    continue
                if end_date and schedule.end_time > end_date:
                    continue
                schedules.append(schedule)
        
        # 按时间排序
        schedules.sort(key=lambda x: x.start_time)
        return schedules
    
    def update_schedule(self, user_id: str, schedule_id: str, updates: dict) -> Optional[ScheduleItem]:
        """更新日程"""
        schedule = self.get_schedule(user_id, schedule_id)
        if not schedule:
            return None
        
        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        schedule.updated_at = datetime.now()
        key = f"schedule:{user_id}:{schedule_id}"
        self.redis.set(key, schedule.model_dump_json())
        
        return schedule
    
    def delete_schedule(self, user_id: str, schedule_id: str) -> bool:
        """删除日程"""
        key = f"schedule:{user_id}:{schedule_id}"
        result = self.redis.delete(key)
        
        if result:
            user_key = f"user:{user_id}:schedules"
            self.redis.srem(user_key, schedule_id)
        
        return result > 0
    
    def check_conflict(self, user_id: str, start_time: datetime, end_time: datetime) -> bool:
        """检查时间冲突"""
        schedules = self.list_schedules(user_id)
        
        for schedule in schedules:
            # 检查时间段是否重叠
            if not (end_time <= schedule.start_time or start_time >= schedule.end_time):
                return True
        
        return False
```

### 4.6 API接口实现

#### 4.6.1 信息解析接口 (`app/api/v1/parse.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from ...core.parser import EntityParser
from ...core.scheduler import ScheduleManager
from ...models.query import ParseRequest

router = APIRouter(prefix="/parse", tags=["信息解析"])

@router.post("/text")
async def parse_text(request: ParseRequest):
    """解析文字内容"""
    parser = EntityParser()
    result = parser.parse_text(request.content)
    
    return {
        "status": "success",
        "data": result
    }

@router.post("/image")
async def parse_image(request: ParseRequest):
    """解析图片内容（课表截图等）"""
    parser = EntityParser()
    
    try:
        result = parser.parse_image(request.content)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片解析失败: {str(e)}")

@router.post("/schedule")
async def parse_and_create_schedule(request: ParseRequest):
    """解析内容并创建日程"""
    parser = EntityParser()
    scheduler = ScheduleManager()
    
    if request.content_type == "image":
        parsed = parser.parse_image(request.content)
    else:
        parsed = parser.parse_text(request.content)
    
    # 创建日程
    from ...models.schedule import ScheduleCreate
    schedule_data = ScheduleCreate(
        event_name=parsed["event_name"],
        start_time=parsed["start_time"].isoformat() if parsed["start_time"] else "",
        end_time=parsed["end_time"].isoformat() if parsed["end_time"] else None,
        location=parsed["location"],
        source=request.content_type,
        priority=parsed["priority"],
        description=parsed["description"]
    )
    
    schedule = scheduler.create_schedule(request.user_id, schedule_data)
    
    return {
        "status": "success",
        "message": "日程创建成功",
        "schedule": schedule.model_dump()
    }
```

### 4.7 QQ机器人实现

#### 4.7.1 NoneBot2机器人 (`bot/campus_bot.py`)

```python
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me
import requests
import os

# 定义命令处理器
parse_cmd = on_command("解析", rule=to_me(), priority=1)
schedule_cmd = on_command("日程", rule=to_me(), priority=1)
query_cmd = on_command("查询", rule=to_me(), priority=1)

@parse_cmd.handle()
async def handle_parse(event: MessageEvent, args: Message = CommandArg()):
    """处理解析命令"""
    content = args.extract_plain_text().strip()
    
    if not content:
        await parse_cmd.finish("请告诉我要解析的内容，比如：\n下周三下午3点教学楼A302开会")
        return
    
    # 调用API解析
    api_url = f"http://localhost:{os.getenv('APP_PORT', 8000)}/api/v1/parse/text"
    response = requests.post(api_url, json={
        "content": content,
        "content_type": "text",
        "user_id": str(event.user_id)
    })
    
    if response.status_code == 200:
        data = response.json()["data"]
        result = f"已解析到以下信息：\n\n"
        result += f"📅 事件：{data['event_name']}\n"
        if data['start_time']:
            result += f"⏰ 时间：{data['start_time']}\n"
        if data['location']:
            result += f"📍 地点：{data['location']}\n"
        result += f"📊 优先级：{data['priority']}\n"
        result += "\n是否需要帮你创建日程？(发送'是'或'否')"
        
        await parse_cmd.send(result)
    else:
        await parse_cmd.finish("解析失败，请稍后重试")

@schedule_cmd.handle()
async def handle_schedule(event: MessageEvent, args: Message = CommandArg()):
    """处理日程命令"""
    action = args.extract_plain_text().strip()
    
    if not action or action == "列表":
        # 获取日程列表
        api_url = f"http://localhost:{os.getenv('APP_PORT', 8000)}/api/v1/schedule/list"
        response = requests.get(api_url, params={"user_id": str(event.user_id)})
        
        if response.status_code == 200:
            schedules = response.json()["data"]
            if not schedules:
                await schedule_cmd.finish("你还没有任何日程安排哦~")
            
            result = "📋 你的日程列表：\n\n"
            for i, schedule in enumerate(schedules, 1):
                result += f"{i}. {schedule['event_name']}\n"
                result += f"   ⏰ {schedule['start_time']} - {schedule['end_time']}\n"
                if schedule['location']:
                    result += f"   📍 {schedule['location']}\n"
                result += "\n"
            
            await schedule_cmd.finish(result)
        else:
            await schedule_cmd.finish("获取日程失败，请稍后重试")
    
    elif action == "创建":
        await schedule_cmd.finish("请发送'解析 + 内容'来创建日程，例如：\n解析 下周三下午3点开会")
    
    else:
        await schedule_cmd.finish("支持的操作：\n- 日程 列表\n- 日程 创建")

@query_cmd.handle()
async def handle_query(event: MessageEvent, args: Message = CommandArg()):
    """处理查询命令"""
    question = args.extract_plain_text().strip()
    
    if not question:
        await query_cmd.finish("请问你想查询什么？\n例如：图书馆开放时间、明天有什么课")
        return
    
    # 调用问答API
    api_url = f"http://localhost:{os.getenv('APP_PORT', 8000)}/api/v1/qa/query"
    response = requests.post(api_url, json={
        "question": question,
        "user_id": str(event.user_id)
    })
    
    if response.status_code == 200:
        answer = response.json()["answer"]
        await query_cmd.finish(answer)
    else:
        await query_cmd.finish("查询失败，请稍后重试")
```

---

## 五、知识库初始化

### 5.1 初始化脚本 (`data/init_data.py`)

```python
import os
import json
from app.core.rag import RAGEngine

def load_knowledge_base():
    """加载知识库数据"""
    rag = RAGEngine()
    
    # 加载校园设施信息
    facilities = [
        {"name": "图书馆", "open_time": "08:00-22:00", "location": "校园中心"},
        {"name": "第一食堂", "open_time": "06:30-21:00", "location": "学生生活区"},
        {"name": "教学楼A", "description": "主要教学楼，包含A101-A500教室"},
        {"name": "体育馆", "open_time": "09:00-21:00", "location": "校园东侧"},
    ]
    
    for facility in facilities:
        content = json.dumps(facility, ensure_ascii=False)
        metadata = {
            "chunk_id": f"facility_{facility['name']}",
            "source_type": "campus_facility",
            "publish_time": "2024-01-01T00:00:00",
            "entity_tags": [facility["name"]],
            "priority": "medium"
        }
        rag.add_document(content, metadata)
        print(f"Added facility: {facility['name']}")
    
    # 加载校历信息
    school_calendar = [
        {"event": "春季学期开学", "date": "2024-02-26"},
        {"event": "清明节放假", "date": "2024-04-04至04-06"},
        {"event": "期中考试周", "date": "2024-04-15至04-19"},
        {"event": "五一劳动节放假", "date": "2024-05-01至05-05"},
        {"event": "期末考试周", "date": "2024-06-17至06-28"},
        {"event": "暑假开始", "date": "2024-07-01"},
    ]
    
    for event in school_calendar:
        content = json.dumps(event, ensure_ascii=False)
        metadata = {
            "chunk_id": f"calendar_{event['event']}",
            "source_type": "school_calendar",
            "publish_time": "2024-01-01T00:00:00",
            "entity_tags": [event["event"]],
            "priority": "high"
        }
        rag.add_document(content, metadata)
        print(f"Added calendar event: {event['event']}")
    
    print("知识库初始化完成！")

if __name__ == "__main__":
    load_knowledge_base()
```

### 5.2 运行初始化

```bash
# 确保虚拟环境已激活
python data/init_data.py
```

---

## 六、启动服务

### 6.1 启动后端API服务

```bash
cd app
python main.py

# 或使用uvicorn直接启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6.2 启动QQ机器人

```bash
cd bot
python campus_bot.py
```

---

## 七、测试验证

### 7.1 API接口测试

#### 7.1.1 测试信息解析

```bash
curl -X POST http://localhost:8000/api/v1/parse/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "下周三下午3点在教学楼A302进行高等数学期中考试",
    "content_type": "text",
    "user_id": "test_user_001"
  }'
```

预期响应：
```json
{
  "status": "success",
  "data": {
    "event_name": "高等数学期中考试",
    "start_time": "2024-01-17T15:00:00",
    "end_time": "2024-01-17T16:00:00",
    "location": "教学楼A302",
    "priority": "high",
    "description": "下周三下午3点在教学楼A302进行高等数学期中考试"
  }
}
```

#### 7.1.2 测试创建日程

```bash
curl -X POST http://localhost:8000/api/v1/schedule/create \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "高等数学期中考试",
    "start_time": "2024-01-17 15:00",
    "end_time": "2024-01-17 17:00",
    "location": "教学楼A302",
    "priority": "high",
    "description": "请携带学生证和2B铅笔"
  }'
```

#### 7.1.3 测试查询日程列表

```bash
curl http://localhost:8000/api/v1/schedule/list?user_id=test_user_001
```

### 7.2 QQ机器人测试

1. **添加机器人为好友**或加入机器人所在频道
2. **发送测试消息**：
   ```
   @校园AI秘书 解析 下周三下午3点教学楼A302开会
   ```
3. **预期回复**：
   ```
   已解析到以下信息：
   
   📅 事件：会议
   ⏰ 时间：2024-01-17 15:00:00
   📍 地点：教学楼A302
   📊 优先级：medium
   
   是否需要帮你创建日程？(发送'是'或'否')
   ```

---

## 八、部署上线

### 8.1 配置反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 8.2 使用Docker Compose部署

创建 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  redis:
    image: redis:7.2
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
  
  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
  
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_HOST=qdrant
      - REDIS_HOST=redis
    depends_on:
      - redis
      - qdrant
    ports:
      - "8000:8000"

volumes:
  redis_data:
  qdrant_data:
```

启动服务：
```bash
docker-compose up -d
```

---

## 九、注意事项

1. **API Key安全**：确保OpenAI API Key不泄露，使用环境变量管理
2. **数据持久化**：定期备份Redis和Qdrant数据
3. **性能监控**：使用Prometheus/Grafana监控服务状态
4. **日志管理**：配置日志轮转，保留足够的历史记录
5. **安全防护**：添加API限流、请求验证等安全措施

---

**文档审核**：已完成  
**适用范围**：开发者、运维人员
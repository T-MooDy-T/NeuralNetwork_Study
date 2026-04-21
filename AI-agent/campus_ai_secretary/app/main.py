"""校园 AI 秘书 - 主服务入口

FastAPI 应用入口，提供 REST API 和提醒服务
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from .api.v1 import router as v1_router
from .api.v1.auth import router as auth_router
from .api.admin import router as admin_router
from .core.scheduler import ScheduleManager
from .core.reminder import ReminderService
from .database.connection import init_db, get_db_stats
from .core.auth import init_admin_user
from .utils.logger import get_logger
from .dependencies import set_scheduler, set_rag_engine
from .middleware import RequestLogMiddleware, SecurityHeadersMiddleware
from .exceptions import global_exception_handler, http_exception_handler

# 配置日志
log = get_logger("campus_ai", os.getenv("LOG_LEVEL", "INFO"))

# 全局服务实例
scheduler: ScheduleManager = None
reminder_service: ReminderService = None
rag_engine: 'RAGEngine' = None  # 延迟类型注解避免循环导入


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global scheduler, reminder_service, rag_engine
    
    # 启动时初始化
    log.info("🚀 校园 AI 秘书 启动中...")
    
    # 初始化数据库
    init_db()
    init_admin_user()
    db_stats = get_db_stats()
    log.info(f"✓ 数据库初始化完成 [{db_stats['type']}]")
    
    # 初始化日程管理器
    scheduler = ScheduleManager(use_memory=True)
    set_scheduler(scheduler)
    log.info("✓ 日程管理器初始化完成")
    
    # 初始化 RAG 引擎
    from .core.rag import RAGEngine
    rag_engine = RAGEngine(use_memory=True)
    set_rag_engine(rag_engine)
    log.info("✓ RAG 引擎初始化完成")
    
    # 初始化提醒服务
    reminder_service = ReminderService(
        scheduler=scheduler,
        check_interval=int(os.getenv("REMINDER_CHECK_INTERVAL", 60))
    )
    reminder_service.start()
    log.info("✓ 提醒服务启动完成")
    
    # 初始化示例数据（Demo 用）
    await init_demo_data()
    
    log.info("✅ 校园 AI 秘书 启动完成!")
    log.info(f"📡 API 地址：http://localhost:{os.getenv('APP_PORT', 8000)}")
    log.info(f"📚 API 文档：http://localhost:{os.getenv('APP_PORT', 8000)}/docs")
    log.info(f"🎨 管理后台：http://localhost:{os.getenv('APP_PORT', 8000)}/admin")
    
    yield
    
    # 关闭时清理
    log.info("👋 校园 AI 秘书 关闭中...")
    if reminder_service:
        reminder_service.stop()
    log.info("✅ 服务已关闭")


async def init_demo_data():
    """初始化示例数据（Demo 用）"""
    global rag_engine
    
    from datetime import datetime, timedelta
    from .models.schedule import ScheduleCreate
    from .database.connection import get_db
    from .database.models import User, Schedule, KnowledgeBase, CollectedInfo, ReminderLog
    
    db = next(get_db())
    
    # 创建测试用户
    test_users = [
        {"username": "test_user1", "email": "test1@example.com", "nickname": "测试用户1", "role": "user"},
        {"username": "test_user2", "email": "test2@example.com", "nickname": "测试用户2", "role": "user"},
        {"username": "test_admin", "email": "admin@example.com", "nickname": "测试管理员", "role": "admin"},
        {"username": "student_zhang", "email": "zhang@university.edu", "nickname": "张三", "role": "user"},
        {"username": "student_li", "email": "li@university.edu", "nickname": "李四", "role": "user"},
        {"username": "teacher_wang", "email": "wang@university.edu", "nickname": "王老师", "role": "admin"}
    ]
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    for user_data in test_users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
                username=user_data["username"],
                password_hash=pwd_context.hash("123456"),
                email=user_data["email"],
                nickname=user_data["nickname"],
                role=user_data["role"],
                is_active=True
            )
            db.add(user)
            db.commit()
            log.info(f"创建测试用户：{user_data['username']}")
    
    # 添加测试日程（使用未来时间）
    now = datetime.now()
    demo_schedules = [
        {
            "event_name": "高等数学期末考试",
            "start_time": (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:00"),
            "end_time": (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:00"),
            "location": "教学楼 A302",
            "priority": "high",
            "description": "请携带学生证和 2B 铅笔"
        },
        {
            "event_name": "计算机实验报告提交",
            "start_time": (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:00"),
            "priority": "high",
            "description": "第 5 次实验报告"
        },
        {
            "event_name": "社团招新宣讲",
            "start_time": (now + timedelta(hours=3)).strftime("%Y-%m-%d %H:00"),
            "location": "学生活动中心 201",
            "priority": "medium"
        },
        {
            "event_name": "班级会议",
            "start_time": (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:00"),
            "location": "教学楼 B105",
            "priority": "medium"
        },
        {
            "event_name": "图书馆学习",
            "start_time": (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:00"),
            "location": "图书馆三楼",
            "priority": "low"
        },
        {
            "event_name": "体育测试",
            "start_time": (now + timedelta(days=1)).strftime("%Y-%m-%d 08:00"),
            "location": "体育场",
            "priority": "high"
        },
        {
            "event_name": "英语四级考试",
            "start_time": (now + timedelta(days=2)).strftime("%Y-%m-%d 09:00"),
            "location": "教学楼 B 区",
            "priority": "high",
            "description": "请携带身份证和准考证"
        },
        {
            "event_name": "毕业设计答辩",
            "start_time": (now + timedelta(days=3)).strftime("%Y-%m-%d 14:00"),
            "location": "综合楼 301",
            "priority": "high",
            "description": "准备 PPT 和论文"
        },
        {
            "event_name": "社团活动日",
            "start_time": (now + timedelta(hours=5)).strftime("%Y-%m-%d %H:00"),
            "location": "学生活动中心",
            "priority": "medium"
        },
        {
            "event_name": "导师见面会",
            "start_time": (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:00"),
            "location": "科研楼 205",
            "priority": "medium"
        }
    ]
    
    for data in demo_schedules:
        try:
            schedule_create = ScheduleCreate(**data)
            scheduler.create_schedule("demo_user", schedule_create)
            log.info(f"添加示例日程：{data['event_name']}")
        except Exception as e:
            log.warning(f"添加示例日程失败：{e}")
    
    # 添加示例知识库（使用全局 RAG 引擎）
    demo_kb = [
        {
            "content": "图书馆开放时间：周一至周五 8:00-22:00，周六日 9:00-21:00。期末期间延长至 24 小时开放。",
            "metadata": {"source_type": "校园设施", "category": "图书馆"}
        },
        {
            "content": "教务处联系方式：电话 010-12345678，邮箱 jwc@university.edu.cn，办公时间工作日 9:00-17:00。",
            "metadata": {"source_type": "校园设施", "category": "教务处"}
        },
        {
            "content": "校医院位于校园北区，24 小时急诊服务。普通门诊时间：周一至周五 8:00-17:00。",
            "metadata": {"source_type": "校园设施", "category": "医院"}
        },
        {
            "content": "食堂就餐时间：早餐 6:30-8:30，午餐 11:00-13:00，晚餐 17:00-19:00。",
            "metadata": {"source_type": "校园设施", "category": "食堂"}
        },
        {
            "content": "期末考试安排已发布，请登录教务系统查看具体考试时间和地点。",
            "metadata": {"source_type": "教务通知", "category": "考试"}
        },
        {
            "content": "校园 Wi-Fi 免费覆盖，连接 SSID: Campus-WiFi，使用学号和密码登录。",
            "metadata": {"source_type": "校园设施", "category": "网络"}
        }
    ]
    
    for doc in demo_kb:
        rag_engine.add_document(doc["content"], doc["metadata"])
    
    log.info(f"添加 {len(demo_kb)} 条示例知识库")
    
    # 添加测试采集信息（未读状态）
    collected_info_list = [
        {
            "source": "计算机学院通知群",
            "source_type": "qq_group",
            "sender": "辅导员张老师",
            "content": "请同学们注意，明天下午2点在教学楼A301进行计算机等级考试模拟，请准时参加。",
            "category": "考试通知",
            "priority": "high",
            "tags": ["考试", "计算机"],
            "timestamp": now - timedelta(hours=1)
        },
        {
            "source": "校园公众号",
            "source_type": "wechat_official",
            "sender": "校园通知",
            "content": "图书馆新增电子资源数据库，包含大量学术期刊和论文，请同学们充分利用。",
            "category": "资源更新",
            "priority": "medium",
            "tags": ["图书馆", "资源"],
            "timestamp": now - timedelta(hours=2)
        },
        {
            "source": "班级微信群",
            "source_type": "wechat_chat",
            "sender": "班长",
            "content": "明天班级聚餐时间改为晚上7点，请大家相互转告。",
            "category": "班级活动",
            "priority": "normal",
            "tags": ["聚餐", "班级"],
            "timestamp": now - timedelta(hours=3)
        },
        {
            "source": "学生会通知群",
            "source_type": "qq_group",
            "sender": "学生会主席",
            "content": "本周五举办校园文化节，欢迎各位同学踊跃参与，有精彩节目和丰厚奖品。",
            "category": "校园活动",
            "priority": "medium",
            "tags": ["文化节", "活动"],
            "timestamp": now - timedelta(hours=4)
        },
        {
            "source": "教务系统",
            "source_type": "wechat_official",
            "sender": "教务处",
            "content": "下学期选课时间已确定，请于下周一登录系统进行选课。",
            "category": "教务通知",
            "priority": "high",
            "tags": ["选课", "教务"],
            "timestamp": now - timedelta(hours=5)
        }
    ]
    
    user = db.query(User).filter(User.username == "test_user1").first()
    if user:
        for info_data in collected_info_list:
            existing = db.query(CollectedInfo).filter(
                CollectedInfo.source == info_data["source"],
                CollectedInfo.content == info_data["content"]
            ).first()
            if not existing:
                info = CollectedInfo(
                    user_id=user.id,
                    source=info_data["source"],
                    source_type=info_data["source_type"],
                    sender=info_data["sender"],
                    content=info_data["content"],
                    category=info_data["category"],
                    priority=info_data["priority"],
                    tags=info_data["tags"],
                    status="unread",
                    timestamp=info_data["timestamp"]
                )
                db.add(info)
        db.commit()
        log.info(f"添加 {len(collected_info_list)} 条测试采集信息")
    
    # 添加测试提醒日志（部分失败状态）
    reminder_logs = [
        {
            "user_id": user.id if user else 1,
            "event_name": "测试提醒1",
            "remind_time": now - timedelta(hours=1),
            "offset": "1h",
            "status": "sent"
        },
        {
            "user_id": user.id if user else 1,
            "event_name": "测试提醒2",
            "remind_time": now - timedelta(hours=2),
            "offset": "30m",
            "status": "failed"
        },
        {
            "user_id": user.id if user else 1,
            "event_name": "测试提醒3",
            "remind_time": now - timedelta(hours=3),
            "offset": "1d",
            "status": "sent"
        }
    ]
    
    for log_data in reminder_logs:
        existing = db.query(ReminderLog).filter(
            ReminderLog.event_name == log_data["event_name"],
            ReminderLog.remind_time == log_data["remind_time"]
        ).first()
        if not existing:
            reminder = ReminderLog(**log_data)
            db.add(reminder)
    db.commit()
    log.info(f"添加 {len(reminder_logs)} 条测试提醒日志")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="校园 AI 秘书",
        description="""基于 AI 的校园日程管理和智能问答服务

**功能特性：**
- 📅 **智能日程管理** - 支持自然语言解析创建日程
- 🔔 **主动提醒系统** - 多级提醒，智能时机选择
- 📚 **RAG 知识库** - 语义检索，智能问答
- 🔐 **用户认证** - JWT 认证，管理员权限管理
- 📊 **管理后台** - 可视化仪表盘，数据统计

**技术栈：**
- FastAPI + Python 3.10+
- Qwen LLM (阿里云 DashScope)
- Qdrant 向量数据库
- SQLAlchemy + MySQL/SQLite
- Redis (可选)
""",
        version="1.0.0",
        lifespan=lifespan,
        contact={
            "name": "Campus AI Secretary",
            "email": "support@campus-ai.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        swagger_ui_parameters={
            "deepLinking": True,
            "defaultModelsExpandDepth": -1,
            "displayOperationId": True,
        }
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 请求日志中间件
    app.add_middleware(RequestLogMiddleware)
    
    # 安全响应头中间件
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 全局异常处理器
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, global_exception_handler)
    
    # 注册路由
    app.include_router(v1_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api")
    
    # 静态文件（管理后台）
    from fastapi.staticfiles import StaticFiles
    admin_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "admin")
    if os.path.exists(admin_path):
        app.mount("/admin", StaticFiles(directory=admin_path, html=True), name="admin")
        log.info(f"✅ 管理后台静态文件挂载成功: {admin_path}")
    else:
        log.warning(f"⚠️ 管理后台目录不存在: {admin_path}")
    
    # 健康检查
    @app.get(
        "/health", 
        tags=["health"],
        summary="健康检查",
        description="检查服务是否正常运行，返回各组件状态"
    )
    async def health_check():
        """检查服务健康状态"""
        return {
            "status": "healthy",
            "scheduler": "initialized" if scheduler else "not_initialized",
            "reminder": "running" if reminder_service and reminder_service.running else "stopped",
            "database": get_db_stats()
        }
    
    # 根路径
    @app.get("/", tags=["root"], summary="服务入口")
    async def root():
        """服务根路径，返回基本信息"""
        return {
            "name": "校园 AI 秘书",
            "version": "1.0.0",
            "description": "基于 AI 的校园日程管理和智能问答服务",
            "docs": "/docs",
            "redoc": "/redoc",
            "admin": "/admin",
            "health": "/health"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )
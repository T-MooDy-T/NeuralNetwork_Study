"""数据库连接配置"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from loguru import logger
from typing import Optional

# 数据库类型枚举
class DatabaseType:
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


def detect_database_type(url: str) -> str:
    """根据 URL 检测数据库类型"""
    url_lower = url.lower()
    if url_lower.startswith("mysql"):
        return DatabaseType.MYSQL
    elif url_lower.startswith("postgresql"):
        return DatabaseType.POSTGRESQL
    elif url_lower.startswith("sqlite"):
        return DatabaseType.SQLITE
    return DatabaseType.SQLITE


def get_database_url() -> str:
    """获取数据库 URL，支持多种配置方式"""
    # 优先从环境变量获取
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    
    # 根据数据库类型选择默认配置
    db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
    
    if db_type == DatabaseType.MYSQL:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "123456")
        name = os.getenv("DB_NAME", "campus_ai")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
    
    elif db_type == DatabaseType.POSTGRESQL:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        name = os.getenv("DB_NAME", "campus_ai")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    else:
        return "sqlite:///./campus_ai.db"


# 获取数据库 URL
DATABASE_URL = get_database_url()
DATABASE_TYPE = detect_database_type(DATABASE_URL)

# 连接池配置
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"


def create_db_engine() -> object:
    """创建数据库引擎"""
    try:
        if DATABASE_TYPE == DatabaseType.SQLITE:
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                echo=os.getenv("DEBUG", "false").lower() == "true"
            )
            logger.info("✅ SQLite 数据库连接成功")
        else:
            engine = create_engine(
                DATABASE_URL,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_recycle=POOL_RECYCLE,
                pool_pre_ping=POOL_PRE_PING,
                echo=os.getenv("DEBUG", "false").lower() == "true"
            )
            db_name = "MySQL" if DATABASE_TYPE == DatabaseType.MYSQL else "PostgreSQL"
            logger.info(f"✅ {db_name} 数据库连接成功")
            logger.info(f"   连接池配置: size={POOL_SIZE}, overflow={MAX_OVERFLOW}, recycle={POOL_RECYCLE}")
        
        return engine
    except Exception as e:
        logger.warning(f"⚠️ {DATABASE_TYPE} 连接失败：{e}")
        logger.info("将使用 SQLite 作为备用数据库")
        return create_engine(
            "sqlite:///./campus_ai.db",
            connect_args={"check_same_thread": False}
        )


# 创建引擎
engine = create_db_engine()

# Session 工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# 线程安全的 Session 工厂（用于多线程场景）
ScopedSession = scoped_session(SessionLocal)

# Base 类
Base = declarative_base()


def get_db():
    """获取数据库会话（FastAPI 依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_scoped_db():
    """获取线程安全的数据库会话"""
    db = ScopedSession()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    from . import models
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库表初始化完成")


def check_db_connection() -> bool:
    """检查数据库连接"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败：{e}")
        return False


def get_db_stats() -> dict:
    """获取数据库统计信息"""
    return {
        "type": DATABASE_TYPE,
        "url": DATABASE_URL,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_recycle": POOL_RECYCLE,
        "pool_pre_ping": POOL_PRE_PING,
        "connected": check_db_connection()
    }

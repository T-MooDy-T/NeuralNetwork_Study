"""数据库连接配置"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

# 数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:123456@localhost:3306/campus_ai?charset=utf8mb4"
)

# 创建引擎
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("✅ MySQL 数据库连接成功")
except Exception as e:
    logger.warning(f"⚠️ MySQL 连接失败：{e}")
    logger.info("将使用 SQLite 作为备用数据库")
    # 备用 SQLite
    engine = create_engine(
        "sqlite:///./campus_ai.db",
        connect_args={"check_same_thread": False}
    )

# Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    from . import models
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库表初始化完成")


def check_db_connection():
    """检查数据库连接"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败：{e}")
        return False

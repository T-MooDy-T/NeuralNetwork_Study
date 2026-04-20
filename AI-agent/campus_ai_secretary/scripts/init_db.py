#!/usr/bin/env python3
"""数据库初始化脚本

用于创建 MySQL 数据库和表结构
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from sqlalchemy import create_engine
from loguru import logger

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "campus_ai")


def create_database():
    """创建数据库"""
    try:
        # 连接到 MySQL（不指定数据库）
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        logger.info(f"✅ 数据库 '{DB_NAME}' 创建成功（或已存在）")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建数据库失败：{e}")
        return False


def init_tables():
    """初始化表结构"""
    try:
        from app.database.connection import engine, Base
        from app.database import models  # 导入模型以注册表
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表结构创建成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建表结构失败：{e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("校园 AI 秘书 - 数据库初始化")
    print("=" * 50)
    print()
    
    print(f"数据库配置:")
    print(f"  主机：{DB_HOST}:{DB_PORT}")
    print(f"  用户：{DB_USER}")
    print(f"  数据库：{DB_NAME}")
    print()
    
    # 1. 创建数据库
    if not create_database():
        print("\n❌ 数据库创建失败，请检查 MySQL 服务是否运行")
        print("   或者修改 .env 文件中的数据库配置")
        return
    
    # 2. 初始化表结构
    if not init_tables():
        print("\n❌ 表结构创建失败")
        return
    
    print()
    print("=" * 50)
    print("✅ 数据库初始化完成!")
    print("=" * 50)
    print()
    print("默认管理员账号:")
    print("  用户名：admin")
    print("  密码：admin123")
    print()
    print("管理后台地址：http://localhost:8000/admin")


if __name__ == "__main__":
    main()

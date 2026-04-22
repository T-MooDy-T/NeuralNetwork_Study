#!/usr/bin/env python3
"""更新用户表，添加岗位匹配相关字段并填充测试数据"""

import sys
import os

# 设置环境变量
os.environ["DATABASE_URL"] = "mysql+pymysql://root:123456@localhost:3306/campus_ai?charset=utf8mb4"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database.connection import create_db_engine, get_db
from app.database.models import User, Base

def update_user_data():
    """更新用户数据，添加岗位匹配相关信息"""
    db = next(get_db())
    
    # 用户信息映射 - 使用数据库中实际的用户名
    user_profiles = {
        "zhangwei": {
            "major": "计算机科学与技术",
            "skills": "Python,Java,JavaScript,SQL,算法",
            "interests": "人工智能,软件开发,数据挖掘",
            "location": "北京"
        },
        "lili": {
            "major": "软件工程",
            "skills": "Java,Spring Boot,MySQL,Redis",
            "interests": "后端开发,系统架构,微服务",
            "location": "上海"
        },
        "wangqiang": {
            "major": "人工智能",
            "skills": "Python,TensorFlow,Pytorch,机器学习",
            "interests": "深度学习,NLP,计算机视觉",
            "location": "深圳"
        },
        "chenmei": {
            "major": "前端开发",
            "skills": "Vue,React,TypeScript,Node.js",
            "interests": "前端框架,性能优化,用户体验",
            "location": "杭州"
        },
        "lihua": {
            "major": "数据科学",
            "skills": "Python,R,数据分析,数据可视化",
            "interests": "大数据,商业智能,数据挖掘",
            "location": "广州"
        },
        "zhaomin": {
            "major": "网络工程",
            "skills": "Linux,网络安全,防火墙,运维",
            "interests": "云计算,网络架构,DevOps",
            "location": "成都"
        },
        "sunyang": {
            "major": "计算机工程",
            "skills": "C++,Go,Docker,Kubernetes",
            "interests": "系统编程,云原生,高性能计算",
            "location": "武汉"
        }
    }
    
    updated_count = 0
    for username, profile in user_profiles.items():
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.major = profile["major"]
            user.skills = profile["skills"]
            user.interests = profile["interests"]
            user.location = profile["location"]
            updated_count += 1
            print("OK: 更新用户:", username)
    
    db.commit()
    print("\nOK: 共更新", updated_count, "个用户")

if __name__ == "__main__":
    print("=== 更新用户数据 ===")
    update_user_data()
    print("\n=== 更新完成 ===")
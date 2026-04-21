"""删除数据库中的重复用户"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import User, Schedule, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_duplicate_users():
    """删除重复的用户记录"""
    db = SessionLocal()
    
    users = db.query(User).order_by(User.username, User.id).all()
    
    seen_usernames = {}
    duplicate_count = 0
    
    for user in users:
        if user.username in seen_usernames:
            print(f"发现重复用户: {user.username} (ID: {user.id}), 保留ID: {seen_usernames[user.username]}")
            
            schedules = db.query(Schedule).filter(Schedule.user_id == user.id).all()
            if schedules:
                print(f"  迁移 {len(schedules)} 条日程到保留用户")
                for schedule in schedules:
                    schedule.user_id = seen_usernames[user.username]
            
            db.delete(user)
            duplicate_count += 1
        else:
            seen_usernames[user.username] = user.id
    
    db.commit()
    print(f"\n清理完成！共删除 {duplicate_count} 个重复用户")
    
    total_users = db.query(User).count()
    print(f"当前用户总数: {total_users}")
    
    return duplicate_count

if __name__ == "__main__":
    delete_duplicate_users()

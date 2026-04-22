"""同步用户数据到学生画像表"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_db, init_db
from app.database.models import User, StudentProfile
from datetime import datetime
from sqlalchemy.orm import Session

def sync_profiles(db: Session):
    """同步用户数据到学生画像表"""
    print("正在同步用户数据到学生画像表...")
    
    db.query(StudentProfile).delete()
    db.commit()
    print("已清空旧的学生画像数据")
    
    users = db.query(User).all()
    profile_count = 0
    
    for user in users:
        if user.username == 'admin':
            continue
            
        profile = StudentProfile(
            user_id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            schedule_count=0,
            preferences='{}',
            created_at=user.created_at or datetime.now()
        )
        db.add(profile)
        profile_count += 1
    
    db.commit()
    print(f"已同步 {profile_count} 个学生画像")
    
    return profile_count

def main():
    """主函数"""
    print("=" * 50)
    print("同步用户数据到学生画像表")
    print("=" * 50)
    
    init_db()
    db = next(get_db())
    
    try:
        sync_profiles(db)
        print("=" * 50)
        print("同步完成！")
        print("=" * 50)
    except Exception as e:
        print(f"同步失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
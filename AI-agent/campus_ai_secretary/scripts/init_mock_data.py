"""初始化所有表的模拟数据"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database.connection import SessionLocal
from app.database.models import User, Schedule, KnowledgeBase, CollectedInfo, ReminderLog
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def clear_all_data(db):
    """按外键依赖顺序删除所有数据"""
    try:
        db.query(ReminderLog).delete()
        db.query(CollectedInfo).delete()
        db.query(Schedule).delete()
        db.query(KnowledgeBase).delete()
        db.query(User).delete()
        db.commit()
        print("已清除所有现有数据")
    except Exception as e:
        print(f"清除数据失败: {e}")
        db.rollback()

def init_users(db):
    """初始化用户数据"""
    users = [
        {
            "username": "admin",
            "password": "admin123",
            "email": "admin@campus.edu",
            "nickname": "管理员",
            "role": "admin",
            "is_active": True
        },
        {
            "username": "student001",
            "password": "123456",
            "email": "student001@campus.edu",
            "nickname": "张三",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student002",
            "password": "123456",
            "email": "student002@campus.edu",
            "nickname": "李四",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student003",
            "password": "123456",
            "email": "student003@campus.edu",
            "nickname": "王五",
            "role": "user",
            "is_active": True
        },
        {
            "username": "teacher001",
            "password": "123456",
            "email": "teacher001@campus.edu",
            "nickname": "王老师",
            "role": "user",
            "is_active": True
        }
    ]
    
    for user_data in users:
        user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            email=user_data["email"],
            nickname=user_data["nickname"],
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        db.add(user)
    
    db.commit()
    print(f"成功添加 {len(users)} 条用户数据")
    return users

def init_schedules(db, users):
    """初始化日程数据"""
    admin = db.query(User).filter(User.username == "admin").first()
    student001 = db.query(User).filter(User.username == "student001").first()
    
    now = datetime.now()
    schedules = [
        {
            "user_id": admin.id,
            "event_name": "周一例会",
            "start_time": now + timedelta(days=(0 - now.weekday() + 7) % 7 + 7, hours=9),
            "end_time": now + timedelta(days=(0 - now.weekday() + 7) % 7 + 7, hours=10),
            "location": "会议室A",
            "source": "user",
            "priority": "high",
            "description": "每周例行工作会议",
            "remind_times": ["1d", "1h"],
            "status": "pending"
        },
        {
            "user_id": admin.id,
            "event_name": "项目评审会",
            "start_time": now + timedelta(days=2, hours=14),
            "end_time": now + timedelta(days=2, hours=16),
            "location": "报告厅",
            "source": "user",
            "priority": "high",
            "description": "期末项目评审",
            "remind_times": ["2d", "3h"],
            "status": "pending"
        },
        {
            "user_id": student001.id,
            "event_name": "高等数学考试",
            "start_time": now + timedelta(days=5, hours=9),
            "end_time": now + timedelta(days=5, hours=11),
            "location": "教学楼B201",
            "source": "user",
            "priority": "high",
            "description": "期中考试",
            "remind_times": ["1d", "12h", "1h"],
            "status": "pending"
        },
        {
            "user_id": student001.id,
            "event_name": "班级聚餐",
            "start_time": now + timedelta(days=7, hours=18),
            "end_time": now + timedelta(days=7, hours=21),
            "location": "南门火锅店",
            "source": "user",
            "priority": "medium",
            "description": "班级团建活动",
            "remind_times": ["3h"],
            "status": "pending"
        },
        {
            "user_id": student001.id,
            "event_name": "图书馆自习",
            "start_time": now + timedelta(days=1, hours=8),
            "end_time": now + timedelta(days=1, hours=12),
            "location": "图书馆三楼",
            "source": "user",
            "priority": "low",
            "description": "复习数据结构",
            "remind_times": ["30m"],
            "status": "pending"
        },
        {
            "user_id": admin.id,
            "event_name": "新生欢迎会",
            "start_time": now + timedelta(days=3, hours=10),
            "end_time": now + timedelta(days=3, hours=12),
            "location": "体育馆",
            "source": "user",
            "priority": "high",
            "description": "2024级新生欢迎会",
            "remind_times": ["1d", "1h"],
            "status": "pending"
        }
    ]
    
    for schedule_data in schedules:
        schedule = Schedule(
            user_id=schedule_data["user_id"],
            event_name=schedule_data["event_name"],
            start_time=schedule_data["start_time"],
            end_time=schedule_data["end_time"],
            location=schedule_data["location"],
            source=schedule_data["source"],
            priority=schedule_data["priority"],
            description=schedule_data["description"],
            remind_times=schedule_data["remind_times"],
            status=schedule_data["status"]
        )
        db.add(schedule)
    
    db.commit()
    print(f"成功添加 {len(schedules)} 条日程数据")

def init_knowledge_base(db):
    """初始化知识库数据"""
    admin = db.query(User).filter(User.username == "admin").first()
    
    now = datetime.now()
    knowledge_items = [
        {
            "title": "图书馆开放时间",
            "content": "图书馆开放时间：周一至周五 8:00-22:00，周六至周日 9:00-21:00。期末考试期间延长至23:00。",
            "source_type": "校园设施",
            "category": "facility",
            "tags": ["图书馆", "开放时间"],
            "priority": "high",
            "valid_from": now - timedelta(days=30),
            "valid_to": now + timedelta(days=365),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "教务系统使用指南",
            "content": "教务系统地址：jw.campus.edu。学生可查询成绩、选课、查看课表。初始密码为身份证后6位，首次登录请修改密码。",
            "source_type": "教务通知",
            "category": "academic",
            "tags": ["教务系统", "成绩查询"],
            "priority": "high",
            "valid_from": now - timedelta(days=90),
            "valid_to": now + timedelta(days=365),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "校园卡充值指南",
            "content": "校园卡可通过校园卡服务中心、自助充值机或APP进行充值。充值机分布在各食堂和教学楼。",
            "source_type": "校园设施",
            "category": "facility",
            "tags": ["校园卡", "充值"],
            "priority": "medium",
            "valid_from": now - timedelta(days=60),
            "valid_to": now + timedelta(days=365),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "社团招新公告",
            "content": "每年9月为社团招新季，各社团在中心广场设摊招新。可关注校园公众号获取最新招新信息。",
            "source_type": "社团公告",
            "category": "social",
            "tags": ["社团", "招新"],
            "priority": "medium",
            "valid_from": now - timedelta(days=15),
            "valid_to": now + timedelta(days=30),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "期末考试安排",
            "content": "期末考试通常在每学期最后两周进行。具体安排可在教务系统查询。请提前做好复习准备。",
            "source_type": "教务通知",
            "category": "academic",
            "tags": ["考试", "复习"],
            "priority": "high",
            "valid_from": now - timedelta(days=7),
            "valid_to": now + timedelta(days=60),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "校园WiFi使用说明",
            "content": "校园WiFi名称为Campus-WiFi，学生账号密码登录。覆盖区域包括教学楼、图书馆、宿舍区。",
            "source_type": "校园设施",
            "category": "facility",
            "tags": ["WiFi", "网络"],
            "priority": "medium",
            "valid_from": now - timedelta(days=30),
            "valid_to": now + timedelta(days=365),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "奖学金申请指南",
            "content": "国家奖学金每年10月申请，需提交成绩单、获奖证书等材料。详情请咨询学生处。",
            "source_type": "教务通知",
            "category": "academic",
            "tags": ["奖学金", "申请"],
            "priority": "high",
            "valid_from": now - timedelta(days=10),
            "valid_to": now + timedelta(days=20),
            "is_active": True,
            "created_by": admin.id
        },
        {
            "title": "食堂就餐须知",
            "content": "学校共有三个食堂，分别位于东、西、北区。支持校园卡和移动支付。早餐供应时间7:00-9:00，午餐11:00-13:30，晚餐17:00-19:30。",
            "source_type": "校园设施",
            "category": "facility",
            "tags": ["食堂", "就餐"],
            "priority": "normal",
            "valid_from": now - timedelta(days=60),
            "valid_to": now + timedelta(days=365),
            "is_active": True,
            "created_by": admin.id
        }
    ]
    
    for item_data in knowledge_items:
        item = KnowledgeBase(
            title=item_data["title"],
            content=item_data["content"],
            source_type=item_data["source_type"],
            category=item_data["category"],
            tags=item_data["tags"],
            priority=item_data["priority"],
            valid_from=item_data["valid_from"],
            valid_to=item_data["valid_to"],
            is_active=item_data["is_active"],
            created_by=item_data["created_by"]
        )
        db.add(item)
    
    db.commit()
    print(f"成功添加 {len(knowledge_items)} 条知识库数据")

def init_collected_info(db):
    """初始化采集信息数据"""
    admin = db.query(User).filter(User.username == "admin").first()
    
    now = datetime.now()
    collected_data = [
        {
            "source": "计算机202班",
            "source_type": "qq_group",
            "sender": "辅导员王老师",
            "content": "明天下午3点在教学楼A302开班会，请准时参加，记得带学生证",
            "category": "event",
            "priority": "high",
            "tags": ["会议", "班会"],
            "status": "unread",
            "timestamp": now - timedelta(hours=1)
        },
        {
            "source": "计算机202班",
            "source_type": "qq_group",
            "sender": "学习委员",
            "content": "高等数学作业截止日期延长到下周一，请大家抓紧时间完成",
            "category": "academic",
            "priority": "high",
            "tags": ["作业", "数学"],
            "status": "unread",
            "timestamp": now - timedelta(hours=2)
        },
        {
            "source": "计算机202班",
            "source_type": "qq_group",
            "sender": "班长",
            "content": "本周日班级聚餐，地点在南门火锅店，下午6点集合",
            "category": "social",
            "priority": "medium",
            "tags": ["聚餐", "社交"],
            "status": "read",
            "timestamp": now - timedelta(hours=5)
        },
        {
            "source": "班级微信群",
            "source_type": "wechat_chat",
            "sender": "团支书",
            "content": "下周三下午2点在团委办公室开团支部会议，请各位团支委参加",
            "category": "event",
            "priority": "medium",
            "tags": ["会议", "团支部"],
            "status": "unread",
            "timestamp": now - timedelta(hours=3)
        },
        {
            "source": "班级微信群",
            "source_type": "wechat_chat",
            "sender": "生活委员",
            "content": "宿舍检查通知：下周二下午3点进行卫生检查，请大家提前整理",
            "category": "notification",
            "priority": "medium",
            "tags": ["通知", "检查"],
            "status": "read",
            "timestamp": now - timedelta(hours=8)
        },
        {
            "source": "校园通知",
            "source_type": "wechat_official",
            "sender": "unknown",
            "content": "关于举办2024年校园科技节的通知：校园科技节将于下周五（10月20日）在体育馆举行，欢迎同学们积极参与各类科技竞赛和展览活动",
            "url": "https://mp.weixin.qq.com/s/example123",
            "category": "event",
            "priority": "high",
            "tags": ["科技节", "活动"],
            "status": "unread",
            "timestamp": now - timedelta(hours=1)
        },
        {
            "source": "校园通知",
            "source_type": "wechat_official",
            "sender": "unknown",
            "content": "图书馆新增电子资源数据库通知：图书馆新增CNKI、万方等多个数据库的访问权限，同学们可以在校内免费使用",
            "url": "https://mp.weixin.qq.com/s/example456",
            "category": "academic",
            "priority": "high",
            "tags": ["图书馆", "数据库"],
            "status": "read",
            "timestamp": now - timedelta(days=1)
        },
        {
            "source": "校园通知",
            "source_type": "wechat_official",
            "sender": "unknown",
            "content": "大学生创业大赛报名开始：第八届大学生创业大赛现已开放报名，截止日期11月1日，丰厚奖金等你拿",
            "url": "https://mp.weixin.qq.com/s/example789",
            "category": "event",
            "priority": "high",
            "tags": ["创业", "比赛"],
            "status": "unread",
            "timestamp": now - timedelta(days=2)
        },
        {
            "source": "校园通知",
            "source_type": "wechat_official",
            "sender": "unknown",
            "content": "食堂新窗口开业通知：北区食堂三楼新开川菜窗口，欢迎同学们品尝",
            "url": "https://mp.weixin.qq.com/s/example000",
            "category": "campus",
            "priority": "normal",
            "tags": ["食堂", "餐饮"],
            "status": "processed",
            "timestamp": now - timedelta(days=3)
        },
        {
            "source": "计算机学院",
            "source_type": "wechat_official",
            "sender": "unknown",
            "content": "学术讲座预告：下周四下午3点，邀请清华大学李教授来我院做人工智能专题讲座，地点在学术报告厅",
            "url": "https://mp.weixin.qq.com/s/lecture123",
            "category": "academic",
            "priority": "high",
            "tags": ["讲座", "人工智能"],
            "status": "unread",
            "timestamp": now - timedelta(hours=4)
        }
    ]
    
    for data in collected_data:
        raw_data_copy = data.copy()
        if isinstance(raw_data_copy.get("timestamp"), datetime):
            raw_data_copy["timestamp"] = raw_data_copy["timestamp"].isoformat()
        
        info = CollectedInfo(
            user_id=admin.id,
            source=data["source"],
            source_type=data["source_type"],
            sender=data["sender"],
            content=data["content"],
            url=data.get("url"),
            category=data["category"],
            priority=data["priority"],
            tags=data["tags"],
            status=data["status"],
            timestamp=data["timestamp"],
            raw_data=raw_data_copy
        )
        db.add(info)
    
    db.commit()
    print(f"成功添加 {len(collected_data)} 条采集信息")

def init_reminder_logs(db):
    """初始化提醒日志数据"""
    admin = db.query(User).filter(User.username == "admin").first()
    schedules = db.query(Schedule).all()
    
    now = datetime.now()
    reminder_logs = [
        {
            "user_id": admin.id,
            "schedule_id": schedules[0].id if schedules else None,
            "remind_time": now - timedelta(hours=2),
            "event_time": now + timedelta(days=1, hours=9),
            "event_name": "周一例会",
            "offset": "1d",
            "status": "sent",
            "message": "您有一个会议'周一例会'将于明天上午9点开始，地点：会议室A"
        },
        {
            "user_id": admin.id,
            "schedule_id": schedules[1].id if len(schedules) > 1 else None,
            "remind_time": now - timedelta(hours=5),
            "event_time": now + timedelta(days=2, hours=14),
            "event_name": "项目评审会",
            "offset": "2d",
            "status": "sent",
            "message": "您有一个会议'项目评审会'将于后天下午2点开始，地点：报告厅"
        },
        {
            "user_id": admin.id,
            "schedule_id": schedules[2].id if len(schedules) > 2 else None,
            "remind_time": now - timedelta(days=1),
            "event_time": now + timedelta(days=5, hours=9),
            "event_name": "高等数学考试",
            "offset": "1d",
            "status": "sent",
            "message": "您有一个考试'高等数学考试'将于5天后上午9点开始，地点：教学楼B201"
        },
        {
            "user_id": admin.id,
            "schedule_id": schedules[3].id if len(schedules) > 3 else None,
            "remind_time": now - timedelta(hours=1),
            "event_time": now + timedelta(hours=2),
            "event_name": "班级聚餐",
            "offset": "3h",
            "status": "sent",
            "message": "您有一个活动'班级聚餐'将于3小时后开始，地点：南门火锅店"
        },
        {
            "user_id": admin.id,
            "schedule_id": None,
            "remind_time": now - timedelta(hours=3),
            "event_time": now + timedelta(hours=1),
            "event_name": "自习提醒",
            "offset": "1h",
            "status": "sent",
            "message": "该去图书馆自习了，记得带上数据结构课本"
        },
        {
            "user_id": admin.id,
            "schedule_id": None,
            "remind_time": now - timedelta(days=2),
            "event_time": now - timedelta(days=1),
            "event_name": "已完成的会议",
            "offset": "1h",
            "status": "sent",
            "message": "您有一个会议'上周例会'将于1小时后开始"
        }
    ]
    
    for log_data in reminder_logs:
        log = ReminderLog(
            user_id=log_data["user_id"],
            schedule_id=log_data["schedule_id"],
            remind_time=log_data["remind_time"],
            event_time=log_data["event_time"],
            event_name=log_data["event_name"],
            offset=log_data["offset"],
            status=log_data["status"],
            message=log_data["message"],
            sent_at=log_data["remind_time"]
        )
        db.add(log)
    
    db.commit()
    print(f"成功添加 {len(reminder_logs)} 条提醒日志")

def main():
    """主函数"""
    print("=" * 50)
    print("校园 AI 秘书 - 模拟数据初始化")
    print("=" * 50)
    print()
    
    db = SessionLocal()
    
    try:
        print("1. 清除现有数据...")
        clear_all_data(db)
        
        print("\n2. 初始化用户数据...")
        users = init_users(db)
        
        print("\n3. 初始化日程数据...")
        init_schedules(db, users)
        
        print("\n4. 初始化知识库数据...")
        init_knowledge_base(db)
        
        print("\n5. 初始化采集信息...")
        init_collected_info(db)
        
        print("\n6. 初始化提醒日志...")
        init_reminder_logs(db)
        
        print("\n" + "=" * 50)
        print("✅ 模拟数据初始化完成!")
        print("=" * 50)
        print()
        print("管理员账号:")
        print("  用户名：admin")
        print("  密码：admin123")
        print()
        print("测试用户:")
        print("  用户名：student001")
        print("  密码：123456")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

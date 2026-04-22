"""初始化测试数据脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 使用MySQL数据库（与服务配置一致）
os.environ["DATABASE_URL"] = "mysql+pymysql://root:123456@localhost:3306/campus_ai?charset=utf8mb4"

from app.database.connection import get_db, init_db
from app.database.models import User, Schedule, KnowledgeBase, ReminderLog, CollectedInfo
from app.core.auth import get_password_hash
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

def clear_all_data(db: Session):
    """清空所有数据"""
    print("正在清空现有数据...")
    db.query(ReminderLog).delete()
    db.query(CollectedInfo).delete()
    db.query(Schedule).delete()
    db.query(KnowledgeBase).delete()
    db.query(User).delete()
    db.commit()
    print("数据清空完成")

def create_users(db: Session):
    """创建测试用户"""
    print("正在创建用户数据...")
    
    users = [
        {
            "username": "admin",
            "nickname": "管理员",
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin",
            "is_active": True
        },
        {
            "username": "zhangwei",
            "nickname": "张伟",
            "email": "zhangwei@example.com",
            "password": "123456",
            "role": "user",
            "is_active": True
        },
        {
            "username": "lili",
            "nickname": "李丽",
            "email": "lili@example.com",
            "password": "123456",
            "role": "user",
            "is_active": True
        },
        {
            "username": "wangqiang",
            "nickname": "王强",
            "email": "wangqiang@example.com",
            "password": "123456",
            "role": "user",
            "is_active": True
        },
        {
            "username": "chenmei",
            "nickname": "陈梅",
            "email": "chenmei@example.com",
            "password": "123456",
            "role": "user",
            "is_active": True
        },
        {
            "username": "lihua",
            "nickname": "李华",
            "email": "lihua@example.com",
            "password": "123456",
            "role": "user",
            "is_active": True
        },
        {
            "username": "zhaomin",
            "nickname": "赵敏",
            "email": "zhaomin@example.com",
            "password": "123456",
            "role": "user",
            "is_active": True
        },
        {
            "username": "sunyang",
            "nickname": "孙杨",
            "email": "sunyang@example.com",
            "password": "123456",
            "role": "user",
            "is_active": False
        }
    ]
    
    for user_data in users:
        user = User(
            username=user_data["username"],
            nickname=user_data["nickname"],
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=datetime.now() - timedelta(days=user_data["username"].__len__())
        )
        db.add(user)
    
    db.commit()
    print(f"创建了 {len(users)} 个用户")
    return users

def create_schedules(db: Session):
    """创建测试日程"""
    print("正在创建日程数据...")
    
    users = db.query(User).filter(User.role == "user").all()
    user_ids = [u.id for u in users]
    
    if len(user_ids) < 6:
        print("警告：用户数量不足，跳过日程创建")
        return
    
    schedules = [
        {"user_id": user_ids[0], "event_name": "高等数学期中考试", "location": "教学楼A301", "start_time": datetime.now() + timedelta(days=2, hours=9), "priority": "high", "status": "pending"},
        {"user_id": user_ids[0], "event_name": "英语听力练习", "location": "图书馆", "start_time": datetime.now() + timedelta(days=1, hours=14), "priority": "medium", "status": "pending"},
        {"user_id": user_ids[1], "event_name": "计算机编程作业提交", "location": "宿舍", "start_time": datetime.now() + timedelta(days=3, hours=23), "priority": "high", "status": "pending"},
        {"user_id": user_ids[1], "event_name": "体育课-篮球", "location": "体育馆", "start_time": datetime.now() + timedelta(days=1, hours=16), "priority": "low", "status": "pending"},
        {"user_id": user_ids[2], "event_name": "数据库课程设计答辩", "location": "实验楼B205", "start_time": datetime.now() + timedelta(days=5, hours=10), "priority": "high", "status": "pending"},
        {"user_id": user_ids[2], "event_name": "社团活动-书法比赛", "location": "学生活动中心", "start_time": datetime.now() + timedelta(days=4, hours=19), "priority": "medium", "status": "pending"},
        {"user_id": user_ids[3], "event_name": "线性代数答疑", "location": "教学楼B102", "start_time": datetime.now() + timedelta(days=1, hours=15), "priority": "medium", "status": "pending"},
        {"user_id": user_ids[3], "event_name": "校园招聘会", "location": "体育馆", "start_time": datetime.now() + timedelta(days=7, hours=9), "priority": "high", "status": "pending"},
        {"user_id": user_ids[4], "event_name": "物理实验报告", "location": "物理实验室", "start_time": datetime.now() + timedelta(days=2, hours=8), "priority": "medium", "status": "completed"},
        {"user_id": user_ids[4], "event_name": "英语口语考试", "location": "语言中心", "start_time": datetime.now() + timedelta(days=6, hours=11), "priority": "high", "status": "pending"},
        {"user_id": user_ids[5], "event_name": "学生会会议", "location": "学生活动中心", "start_time": datetime.now() + timedelta(days=1, hours=12), "priority": "medium", "status": "pending"},
        {"user_id": user_ids[5], "event_name": "期末考试复习", "location": "图书馆", "start_time": datetime.now() + timedelta(days=10, hours=8), "priority": "high", "status": "pending"}
    ]
    
    for schedule_data in schedules:
        schedule = Schedule(
            user_id=schedule_data["user_id"],
            event_name=schedule_data["event_name"],
            location=schedule_data["location"],
            start_time=schedule_data["start_time"],
            priority=schedule_data["priority"],
            status=schedule_data["status"],
            created_at=datetime.now() - timedelta(hours=schedule_data["user_id"] * 2)
        )
        db.add(schedule)
    
    db.commit()
    print(f"创建了 {len(schedules)} 个日程")

def create_knowledge(db: Session):
    """创建测试知识库"""
    print("正在创建知识库数据...")
    
    knowledge_items = [
        {
            "title": "高等数学复习指南",
            "content": "第一章 函数与极限\n1.1 函数的概念\n函数是数学中最重要的概念之一...\n\n第二章 导数与微分\n2.1 导数的定义...",
            "source_type": "学习资料",
            "category": "数学",
            "is_active": True,
            "view_count": 156
        },
        {
            "title": "Python编程入门",
            "content": "Python是一种高级编程语言，以其简洁的语法和强大的功能著称...\n\n基础语法:\n- 变量定义\n- 数据类型\n- 控制流程",
            "source_type": "学习资料",
            "category": "计算机",
            "is_active": True,
            "view_count": 234
        },
        {
            "title": "校园图书馆使用指南",
            "content": "图书馆开放时间:\n周一至周五: 8:00-22:00\n周末: 9:00-20:00\n\n借书规则:\n- 本科生可借10本，期限30天\n- 研究生可借20本，期限60天",
            "source_type": "通知公告",
            "category": "校园服务",
            "is_active": True,
            "view_count": 89
        },
        {
            "title": "大学生心理健康指南",
            "content": "大学生常见心理问题:\n1. 学业压力\n2. 人际关系\n3. 就业焦虑\n\n心理咨询中心地址: 学生活动中心302室\n预约电话: 010-12345678",
            "source_type": "通知公告",
            "category": "心理健康",
            "is_active": True,
            "view_count": 45
        },
        {
            "title": "英语四六级备考攻略",
            "content": "听力部分技巧:\n- 提前浏览选项\n- 注意关键词\n- 边听边记笔记\n\n阅读部分技巧:\n- 先看问题再读文章\n- 注意转折词",
            "source_type": "学习资料",
            "category": "英语",
            "is_active": True,
            "view_count": 312
        },
        {
            "title": "校园招聘会时间表",
            "content": "3月15日: 华为公司宣讲会\n地点: 学术报告厅\n时间: 14:00-16:00\n\n3月20日: 腾讯公司宣讲会\n地点: 大学生活动中心\n时间: 10:00-12:00",
            "source_type": "通知公告",
            "category": "就业",
            "is_active": True,
            "view_count": 267
        },
        {
            "title": "数据结构复习笔记",
            "content": "链表:\n- 单链表\n- 双链表\n- 循环链表\n\n树:\n- 二叉树\n- 二叉搜索树\n- AVL树",
            "source_type": "学习资料",
            "category": "计算机",
            "is_active": True,
            "view_count": 178
        },
        {
            "title": "校园体育设施开放时间",
            "content": "体育馆:\n周一至周五: 6:00-22:00\n周末: 8:00-22:00\n\n游泳馆:\n周一至周五: 12:00-21:00\n周末: 10:00-22:00",
            "source_type": "通知公告",
            "category": "体育",
            "is_active": True,
            "view_count": 56
        }
    ]
    
    for kb_data in knowledge_items:
        kb = KnowledgeBase(
            title=kb_data["title"],
            content=kb_data["content"],
            source_type=kb_data["source_type"],
            category=kb_data["category"],
            is_active=kb_data["is_active"],
            view_count=kb_data["view_count"],
            created_at=datetime.now() - timedelta(days=kb_data["view_count"] % 10)
        )
        db.add(kb)
    
    db.commit()
    print(f"创建了 {len(knowledge_items)} 条知识库")

def create_collected_info(db: Session):
    """创建测试采集信息"""
    print("正在创建采集信息...")
    
    collected_items = [
        {"source": "QQ群-计算机学院通知", "source_type": "qq_group", "sender": "辅导员", "content": "本周六下午2点在学术报告厅举行优秀毕业生经验分享会，请同学们积极参加。", "priority": "high", "status": "unread"},
        {"source": "微信公众号-校园头条", "source_type": "wechat_official", "sender": "校园头条", "content": "春季运动会将于下月初举行，现在开始接受报名，报名截止日期为本周五。", "priority": "medium", "status": "unread"},
        {"source": "QQ群-班级群", "source_type": "qq_group", "sender": "班长", "content": "明天下午的课程因故取消，请大家互相转告。", "priority": "high", "status": "read"},
        {"source": "微信群-学生会", "source_type": "wechat_chat", "sender": "学生会主席", "content": "下周三组织志愿者活动，有意向的同学请在群里报名。", "priority": "medium", "status": "unread"},
        {"source": "微信公众号-图书馆", "source_type": "wechat_official", "sender": "图书馆", "content": "新书推荐：《Python数据分析实战》已到馆，欢迎借阅。", "priority": "low", "status": "read"},
        {"source": "QQ群-考研交流群", "source_type": "qq_group", "sender": "管理员", "content": "考研倒计时100天，大家加油！分享一些备考经验...", "priority": "medium", "status": "unread"},
        {"source": "微信群-室友群", "source_type": "wechat_chat", "sender": "室友小王", "content": "今晚一起去食堂吃饭吗？", "priority": "low", "status": "read"},
        {"source": "微信公众号-就业指导中心", "source_type": "wechat_official", "sender": "就业指导中心", "content": "下周将举办简历制作培训讲座，欢迎参加。", "priority": "medium", "status": "unread"},
        {"source": "QQ群-社团联合会", "source_type": "qq_group", "sender": "社联主席", "content": "社团招新即将开始，请各社团做好准备。", "priority": "high", "status": "unread"},
        {"source": "微信公众号-校园生活", "source_type": "wechat_official", "sender": "校园生活", "content": "校园超市新到一批进口零食，欢迎选购。", "priority": "low", "status": "read"}
    ]
    
    for item_data in collected_items:
        item = CollectedInfo(
            source=item_data["source"],
            source_type=item_data["source_type"],
            sender=item_data["sender"],
            content=item_data["content"],
            priority=item_data["priority"],
            status=item_data["status"],
            timestamp=datetime.now() - timedelta(hours=collected_items.index(item_data) * 3)
        )
        db.add(item)
    
    db.commit()
    print(f"创建了 {len(collected_items)} 条采集信息")

def create_reminders(db: Session):
    """创建测试提醒日志"""
    print("正在创建提醒日志...")
    
    users = db.query(User).filter(User.role == "user").all()
    user_ids = [u.id for u in users]
    
    schedules = db.query(Schedule).all()
    schedule_ids = [s.id for s in schedules]
    
    if len(user_ids) < 6 or len(schedule_ids) < 12:
        print("警告：用户或日程数量不足，跳过提醒日志创建")
        return
    
    reminders = [
        {"user_id": user_ids[0], "schedule_id": schedule_ids[0], "event_name": "高等数学期中考试", "remind_time": datetime.now() + timedelta(days=2, hours=8), "status": "pending"},
        {"user_id": user_ids[0], "schedule_id": schedule_ids[1], "event_name": "英语听力练习", "remind_time": datetime.now() + timedelta(days=1, hours=13), "status": "pending"},
        {"user_id": user_ids[1], "schedule_id": schedule_ids[2], "event_name": "计算机编程作业提交", "remind_time": datetime.now() + timedelta(days=3, hours=22), "status": "pending"},
        {"user_id": user_ids[2], "schedule_id": schedule_ids[4], "event_name": "数据库课程设计答辩", "remind_time": datetime.now() + timedelta(days=5, hours=9), "status": "pending"},
        {"user_id": user_ids[3], "schedule_id": schedule_ids[7], "event_name": "校园招聘会", "remind_time": datetime.now() + timedelta(days=7, hours=8), "status": "pending"},
        {"user_id": user_ids[4], "schedule_id": schedule_ids[9], "event_name": "英语口语考试", "remind_time": datetime.now() + timedelta(days=6, hours=10), "status": "pending"},
        {"user_id": user_ids[1], "schedule_id": schedule_ids[5], "event_name": "社团活动-书法比赛", "remind_time": datetime.now() + timedelta(days=4, hours=18), "status": "sent", "sent_at": datetime.now() - timedelta(hours=2)},
        {"user_id": user_ids[3], "schedule_id": schedule_ids[6], "event_name": "线性代数答疑", "remind_time": datetime.now() + timedelta(days=1, hours=14), "status": "sent", "sent_at": datetime.now() - timedelta(hours=5)},
        {"user_id": user_ids[4], "schedule_id": schedule_ids[8], "event_name": "物理实验报告", "remind_time": datetime.now() + timedelta(days=2, hours=7), "status": "sent", "sent_at": datetime.now() - timedelta(days=1)},
        {"user_id": user_ids[5], "schedule_id": schedule_ids[10], "event_name": "学生会会议", "remind_time": datetime.now() + timedelta(days=1, hours=11), "status": "sent", "sent_at": datetime.now() - timedelta(hours=3)}
    ]
    
    for reminder_data in reminders:
        reminder = ReminderLog(
            user_id=reminder_data["user_id"],
            schedule_id=reminder_data["schedule_id"],
            event_name=reminder_data["event_name"],
            remind_time=reminder_data["remind_time"],
            status=reminder_data["status"],
            sent_at=reminder_data.get("sent_at")
        )
        db.add(reminder)
    
    db.commit()
    print(f"创建了 {len(reminders)} 条提醒日志")

def main():
    """主函数"""
    print("=" * 50)
    print("初始化校园AI秘书测试数据")
    print("=" * 50)
    
    # 初始化数据库
    init_db()
    
    # 获取数据库连接
    db = next(get_db())
    
    try:
        # 清空现有数据
        clear_all_data(db)
        
        # 创建测试数据
        create_users(db)
        create_schedules(db)
        create_knowledge(db)
        create_collected_info(db)
        create_reminders(db)
        
        print("=" * 50)
        print("测试数据初始化完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
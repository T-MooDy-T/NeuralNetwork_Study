"""生成学生画像模拟数据"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import User, Schedule, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_mock_users():
    """创建模拟学生用户"""
    db = SessionLocal()
    
    students = [
        {
            "username": "student001",
            "nickname": "张小明",
            "email": "zhangxm@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student002",
            "nickname": "李婷婷",
            "email": "litt@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student003",
            "nickname": "王大力",
            "email": "wangdl@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student004",
            "nickname": "赵晓雯",
            "email": "zhaoxw@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student005",
            "nickname": "陈浩然",
            "email": "chenhr@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student006",
            "nickname": "刘雨萱",
            "email": "liuyx@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student007",
            "nickname": "周俊杰",
            "email": "zhoujj@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        },
        {
            "username": "student008",
            "nickname": "吴佳怡",
            "email": "wujiay@university.edu",
            "password_hash": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q",
            "role": "user",
            "is_active": True
        }
    ]
    
    for student in students:
        existing = db.query(User).filter(User.username == student["username"]).first()
        if not existing:
            user = User(**student)
            db.add(user)
    
    db.commit()
    print("模拟用户创建完成")
    return db.query(User).filter(User.role == "user").all()

def create_mock_schedules(students):
    """为学生创建模拟日程"""
    db = SessionLocal()
    
    schedule_templates = {
        "student001": [
            {"event_name": "高等数学课程", "start_time": datetime.now() - timedelta(days=5, hours=9), "location": "教学楼A101", "description": "微积分复习", "priority": "high", "status": "completed"},
            {"event_name": "英语四级备考", "start_time": datetime.now() - timedelta(days=4, hours=14), "location": "图书馆", "description": "听力练习", "priority": "medium", "status": "completed"},
            {"event_name": "篮球社团活动", "start_time": datetime.now() - timedelta(days=3, hours=16), "location": "体育馆", "description": "每周训练", "priority": "low", "status": "completed"},
            {"event_name": "数据结构作业", "start_time": datetime.now() - timedelta(days=2, hours=10), "location": "实验室", "description": "完成链表实现", "priority": "high", "status": "completed"},
            {"event_name": "班级聚餐", "start_time": datetime.now() - timedelta(days=1, hours=18), "location": "学校餐厅", "description": "庆祝考试结束", "priority": "medium", "status": "completed"},
            {"event_name": "Python编程学习", "start_time": datetime.now() + timedelta(hours=2), "location": "宿舍", "description": "学习Django框架", "priority": "high", "status": "pending"},
            {"event_name": "羽毛球运动", "start_time": datetime.now() + timedelta(days=1, hours=15), "location": "体育馆", "description": "和同学一起打球", "priority": "low", "status": "pending"},
            {"event_name": "期末考试复习", "start_time": datetime.now() + timedelta(days=2, hours=9), "location": "图书馆", "description": "复习线性代数", "priority": "high", "status": "pending"},
            {"event_name": "编程竞赛准备", "start_time": datetime.now() + timedelta(days=3, hours=14), "location": "实验室", "description": "算法练习", "priority": "high", "status": "pending"},
            {"event_name": "社团招新", "start_time": datetime.now() + timedelta(days=5, hours=10), "location": "活动中心", "description": "计算机协会招新", "priority": "medium", "status": "pending"}
        ],
        "student002": [
            {"event_name": "英语口语练习", "start_time": datetime.now() - timedelta(days=5, hours=8), "location": "语音室", "description": "外教对话", "priority": "high", "status": "completed"},
            {"event_name": "舞蹈社团排练", "start_time": datetime.now() - timedelta(days=4, hours=19), "location": "活动中心", "description": "迎新晚会准备", "priority": "medium", "status": "completed"},
            {"event_name": "大学物理实验", "start_time": datetime.now() - timedelta(days=3, hours=10), "location": "物理实验室", "description": "光学实验", "priority": "high", "status": "completed"},
            {"event_name": "校园音乐会", "start_time": datetime.now() - timedelta(days=2, hours=19), "location": "大礼堂", "description": "观看演出", "priority": "low", "status": "completed"},
            {"event_name": "专业课作业", "start_time": datetime.now() - timedelta(days=1, hours=14), "location": "宿舍", "description": "市场营销案例分析", "priority": "medium", "status": "completed"},
            {"event_name": "瑜伽课程", "start_time": datetime.now() + timedelta(hours=3), "location": "体育馆", "description": "放松身心", "priority": "low", "status": "pending"},
            {"event_name": "小组项目讨论", "start_time": datetime.now() + timedelta(days=1, hours=14), "location": "教学楼", "description": "准备期末答辩", "priority": "high", "status": "pending"},
            {"event_name": "生日聚会", "start_time": datetime.now() + timedelta(days=3, hours=18), "location": "校外餐厅", "description": "庆祝生日", "priority": "medium", "status": "pending"},
            {"event_name": "英语角", "start_time": datetime.now() + timedelta(days=4, hours=16), "location": "图书馆", "description": "英语口语交流", "priority": "medium", "status": "pending"},
            {"event_name": "舞蹈表演", "start_time": datetime.now() + timedelta(days=6, hours=19), "location": "大礼堂", "description": "迎新晚会演出", "priority": "high", "status": "pending"}
        ],
        "student003": [
            {"event_name": "足球比赛", "start_time": datetime.now() - timedelta(days=5, hours=15), "location": "足球场", "description": "校联赛", "priority": "high", "status": "completed"},
            {"event_name": "计算机网络课程", "start_time": datetime.now() - timedelta(days=4, hours=10), "location": "教学楼B203", "description": "TCP/IP协议", "priority": "medium", "status": "completed"},
            {"event_name": "图书馆自习", "start_time": datetime.now() - timedelta(days=3, hours=9), "location": "图书馆", "description": "复习备考", "priority": "high", "status": "completed"},
            {"event_name": "游戏社团活动", "start_time": datetime.now() - timedelta(days=2, hours=20), "location": "活动中心", "description": "电竞比赛", "priority": "low", "status": "completed"},
            {"event_name": "高数习题课", "start_time": datetime.now() - timedelta(days=1, hours=11), "location": "教学楼", "description": "难题讲解", "priority": "high", "status": "completed"},
            {"event_name": "健身房锻炼", "start_time": datetime.now() + timedelta(hours=1), "location": "体育馆", "description": "力量训练", "priority": "medium", "status": "pending"},
            {"event_name": "编程竞赛准备", "start_time": datetime.now() + timedelta(days=1, hours=14), "location": "实验室", "description": "算法练习", "priority": "high", "status": "pending"},
            {"event_name": "朋友聚会", "start_time": datetime.now() + timedelta(days=2, hours=18), "location": "咖啡厅", "description": "周末休闲", "priority": "low", "status": "pending"},
            {"event_name": "足球训练", "start_time": datetime.now() + timedelta(days=4, hours=15), "location": "足球场", "description": "赛前训练", "priority": "high", "status": "pending"},
            {"event_name": "游戏开发分享", "start_time": datetime.now() + timedelta(days=5, hours=19), "location": "活动中心", "description": "Unity游戏开发", "priority": "medium", "status": "pending"}
        ],
        "student004": [
            {"event_name": "化学实验", "start_time": datetime.now() - timedelta(days=5, hours=9), "location": "化学实验室", "description": "有机合成实验", "priority": "high", "status": "completed"},
            {"event_name": "学生会会议", "start_time": datetime.now() - timedelta(days=4, hours=14), "location": "学生会办公室", "description": "活动策划", "priority": "medium", "status": "completed"},
            {"event_name": "钢琴练习", "start_time": datetime.now() - timedelta(days=3, hours=17), "location": "音乐教室", "description": "考级准备", "priority": "high", "status": "completed"},
            {"event_name": "校园志愿者活动", "start_time": datetime.now() - timedelta(days=2, hours=10), "location": "图书馆", "description": "整理图书", "priority": "low", "status": "completed"},
            {"event_name": "英语阅读", "start_time": datetime.now() - timedelta(days=1, hours=15), "location": "宿舍", "description": "阅读英文原著", "priority": "medium", "status": "completed"},
            {"event_name": "备考雅思", "start_time": datetime.now() + timedelta(hours=4), "location": "图书馆", "description": "写作练习", "priority": "high", "status": "pending"},
            {"event_name": "音乐会演出", "start_time": datetime.now() + timedelta(days=2, hours=19), "location": "大礼堂", "description": "钢琴独奏", "priority": "high", "status": "pending"},
            {"event_name": "电影欣赏", "start_time": datetime.now() + timedelta(days=4, hours=19), "location": "电影院", "description": "周末观影", "priority": "low", "status": "pending"},
            {"event_name": "学生会活动", "start_time": datetime.now() + timedelta(days=5, hours=14), "location": "活动中心", "description": "志愿者招募", "priority": "medium", "status": "pending"},
            {"event_name": "钢琴考级", "start_time": datetime.now() + timedelta(days=7, hours=10), "location": "音乐楼", "description": "钢琴八级考试", "priority": "high", "status": "pending"}
        ],
        "student005": [
            {"event_name": "数学建模竞赛", "start_time": datetime.now() - timedelta(days=5, hours=9), "location": "实验室", "description": "团队讨论", "priority": "high", "status": "completed"},
            {"event_name": "数据库课程", "start_time": datetime.now() - timedelta(days=4, hours=14), "location": "教学楼C301", "description": "SQL优化", "priority": "medium", "status": "completed"},
            {"event_name": "跑步锻炼", "start_time": datetime.now() - timedelta(days=3, hours=7), "location": "操场", "description": "晨跑", "priority": "low", "status": "completed"},
            {"event_name": "创业讲座", "start_time": datetime.now() - timedelta(days=2, hours=19), "location": "大礼堂", "description": "校友分享", "priority": "medium", "status": "completed"},
            {"event_name": "毕业设计", "start_time": datetime.now() - timedelta(days=1, hours=10), "location": "实验室", "description": "论文撰写", "priority": "high", "status": "completed"},
            {"event_name": "人工智能学习", "start_time": datetime.now() + timedelta(hours=2), "location": "宿舍", "description": "深度学习入门", "priority": "high", "status": "pending"},
            {"event_name": "篮球友谊赛", "start_time": datetime.now() + timedelta(days=1, hours=16), "location": "篮球场", "description": "和外校交流", "priority": "medium", "status": "pending"},
            {"event_name": "技术分享会", "start_time": datetime.now() + timedelta(days=3, hours=14), "location": "教学楼", "description": "AI技术讲座", "priority": "high", "status": "pending"},
            {"event_name": "数学建模培训", "start_time": datetime.now() + timedelta(days=5, hours=9), "location": "实验室", "description": "备战竞赛", "priority": "high", "status": "pending"},
            {"event_name": "创业大赛", "start_time": datetime.now() + timedelta(days=7, hours=10), "location": "大礼堂", "description": "项目路演", "priority": "high", "status": "pending"}
        ],
        "student006": [
            {"event_name": "中文写作课", "start_time": datetime.now() - timedelta(days=5, hours=10), "location": "教学楼D102", "description": "散文写作", "priority": "medium", "status": "completed"},
            {"event_name": "古筝练习", "start_time": datetime.now() - timedelta(days=4, hours=16), "location": "音乐教室", "description": "考级曲目练习", "priority": "high", "status": "completed"},
            {"event_name": "读书会", "start_time": datetime.now() - timedelta(days=3, hours=15), "location": "图书馆", "description": "文学作品讨论", "priority": "low", "status": "completed"},
            {"event_name": "摄影社团活动", "start_time": datetime.now() - timedelta(days=2, hours=14), "location": "校园", "description": "风景摄影", "priority": "low", "status": "completed"},
            {"event_name": "古代文学", "start_time": datetime.now() - timedelta(days=1, hours=9), "location": "教学楼", "description": "唐诗宋词", "priority": "high", "status": "completed"},
            {"event_name": "古筝演出", "start_time": datetime.now() + timedelta(hours=3), "location": "大礼堂", "description": "校园音乐会", "priority": "high", "status": "pending"},
            {"event_name": "写作比赛", "start_time": datetime.now() + timedelta(days=2, hours=14), "location": "教学楼", "description": "校园文学大赛", "priority": "medium", "status": "pending"},
            {"event_name": "摄影展览", "start_time": datetime.now() + timedelta(days=4, hours=10), "location": "图书馆", "description": "个人摄影展", "priority": "medium", "status": "pending"},
            {"event_name": "诗词朗诵", "start_time": datetime.now() + timedelta(days=5, hours=19), "location": "活动中心", "description": "经典诗词朗诵会", "priority": "low", "status": "pending"},
            {"event_name": "古筝考级", "start_time": datetime.now() + timedelta(days=7, hours=10), "location": "音乐楼", "description": "古筝十级考试", "priority": "high", "status": "pending"}
        ],
        "student007": [
            {"event_name": "机器学习课程", "start_time": datetime.now() - timedelta(days=5, hours=14), "location": "实验室", "description": "神经网络", "priority": "high", "status": "completed"},
            {"event_name": "机器人社团", "start_time": datetime.now() - timedelta(days=4, hours=16), "location": "工程楼", "description": "机器人组装", "priority": "medium", "status": "completed"},
            {"event_name": "算法竞赛", "start_time": datetime.now() - timedelta(days=3, hours=9), "location": "教学楼", "description": "ACM选拔赛", "priority": "high", "status": "completed"},
            {"event_name": "围棋社活动", "start_time": datetime.now() - timedelta(days=2, hours=15), "location": "活动中心", "description": "围棋对弈", "priority": "low", "status": "completed"},
            {"event_name": "数据挖掘", "start_time": datetime.now() - timedelta(days=1, hours=10), "location": "实验室", "description": "大数据分析", "priority": "high", "status": "completed"},
            {"event_name": "AI项目开发", "start_time": datetime.now() + timedelta(hours=2), "location": "实验室", "description": "深度学习项目", "priority": "high", "status": "pending"},
            {"event_name": "机器人比赛", "start_time": datetime.now() + timedelta(days=3, hours=9), "location": "工程楼", "description": "机器人足球赛", "priority": "high", "status": "pending"},
            {"event_name": "围棋比赛", "start_time": datetime.now() + timedelta(days=5, hours=14), "location": "活动中心", "description": "校园围棋联赛", "priority": "medium", "status": "pending"},
            {"event_name": "技术论坛", "start_time": datetime.now() + timedelta(days=6, hours=19), "location": "大礼堂", "description": "AI技术分享", "priority": "high", "status": "pending"},
            {"event_name": "毕业设计答辩", "start_time": datetime.now() + timedelta(days=10, hours=10), "location": "教学楼", "description": "论文答辩", "priority": "high", "status": "pending"}
        ],
        "student008": [
            {"event_name": "绘画课", "start_time": datetime.now() - timedelta(days=5, hours=14), "location": "美术楼", "description": "素描基础", "priority": "medium", "status": "completed"},
            {"event_name": "动漫社活动", "start_time": datetime.now() - timedelta(days=4, hours=19), "location": "活动中心", "description": "漫画创作", "priority": "low", "status": "completed"},
            {"event_name": "设计软件学习", "start_time": datetime.now() - timedelta(days=3, hours=10), "location": "计算机房", "description": "Photoshop练习", "priority": "high", "status": "completed"},
            {"event_name": "手工制作", "start_time": datetime.now() - timedelta(days=2, hours=15), "location": "美术楼", "description": "陶艺制作", "priority": "low", "status": "completed"},
            {"event_name": "艺术史", "start_time": datetime.now() - timedelta(days=1, hours=9), "location": "教学楼", "description": "西方艺术史", "priority": "medium", "status": "completed"},
            {"event_name": "插画创作", "start_time": datetime.now() + timedelta(hours=3), "location": "美术楼", "description": "原创插画", "priority": "high", "status": "pending"},
            {"event_name": "动漫展览", "start_time": datetime.now() + timedelta(days=2, hours=10), "location": "图书馆", "description": "动漫作品展示", "priority": "medium", "status": "pending"},
            {"event_name": "设计比赛", "start_time": datetime.now() + timedelta(days=4, hours=14), "location": "美术楼", "description": "校园设计大赛", "priority": "high", "status": "pending"},
            {"event_name": "手工市集", "start_time": datetime.now() + timedelta(days=5, hours=16), "location": "校园广场", "description": "手工艺品售卖", "priority": "low", "status": "pending"},
            {"event_name": "毕业作品展", "start_time": datetime.now() + timedelta(days=8, hours=10), "location": "美术楼", "description": "毕业设计展览", "priority": "high", "status": "pending"}
        ]
    }
    
    for student in students:
        templates = schedule_templates.get(student.username, [])
        for template in templates:
            existing = db.query(Schedule).filter(
                Schedule.user_id == student.id,
                Schedule.event_name == template["event_name"]
            ).first()
            if not existing:
                schedule = Schedule(
                    user_id=student.id,
                    **template
                )
                db.add(schedule)
    
    db.commit()
    print("模拟日程创建完成")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    students = create_mock_users()
    create_mock_schedules(students)
    print("所有模拟数据创建完成！")

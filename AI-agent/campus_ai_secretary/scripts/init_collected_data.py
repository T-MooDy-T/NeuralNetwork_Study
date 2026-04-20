"""初始化采集信息模拟数据"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database.connection import SessionLocal, init_db
from app.database.models import CollectedInfo, User

def init_collected_data():
    """初始化采集信息模拟数据"""
    db = SessionLocal()
    
    try:
        # 查找admin用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("未找到admin用户")
            return
        
        # 删除现有数据
        db.query(CollectedInfo).delete()
        db.commit()
        print("已清除现有采集数据")
        
        # 模拟数据
        mock_data = [
            # QQ群消息
            {
                "source": "计算机202班",
                "source_type": "qq_group",
                "sender": "辅导员王老师",
                "content": "明天下午3点在教学楼A302开班会，请准时参加，记得带学生证",
                "category": "event",
                "priority": "high",
                "tags": ["会议", "班会"],
                "timestamp": datetime.now()
            },
            {
                "source": "计算机202班",
                "source_type": "qq_group",
                "sender": "学习委员",
                "content": "高等数学作业截止日期延长到下周一，请大家抓紧时间完成",
                "category": "academic",
                "priority": "high",
                "tags": ["作业", "数学"],
                "timestamp": datetime.now() - timedelta(hours=2)
            },
            {
                "source": "计算机202班",
                "source_type": "qq_group",
                "sender": "班长",
                "content": "本周日班级聚餐，地点在南门火锅店，下午6点集合",
                "category": "social",
                "priority": "medium",
                "tags": ["聚餐", "社交"],
                "timestamp": datetime.now() - timedelta(hours=5)
            },
            # 微信群消息
            {
                "source": "班级微信群",
                "source_type": "wechat_chat",
                "sender": "团支书",
                "content": "下周三下午2点在团委办公室开团支部会议，请各位团支委参加",
                "category": "event",
                "priority": "medium",
                "tags": ["会议", "团支部"],
                "timestamp": datetime.now() - timedelta(hours=3)
            },
            {
                "source": "班级微信群",
                "source_type": "wechat_chat",
                "sender": "生活委员",
                "content": "宿舍检查通知：下周二下午3点进行卫生检查，请大家提前整理",
                "category": "notification",
                "priority": "medium",
                "tags": ["通知", "检查"],
                "timestamp": datetime.now() - timedelta(hours=8)
            },
            # 公众号文章
            {
                "source": "校园通知",
                "source_type": "wechat_official",
                "sender": "unknown",
                "content": "关于举办2024年校园科技节的通知：校园科技节将于下周五（10月20日）在体育馆举行，欢迎同学们积极参与各类科技竞赛和展览活动",
                "url": "https://mp.weixin.qq.com/s/example123",
                "category": "event",
                "priority": "high",
                "tags": ["科技节", "活动"],
                "timestamp": datetime.now() - timedelta(hours=1)
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
                "timestamp": datetime.now() - timedelta(days=1)
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
                "timestamp": datetime.now() - timedelta(days=2)
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
                "timestamp": datetime.now() - timedelta(days=3)
            }
        ]
        
        # 添加数据
        for data in mock_data:
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
                timestamp=data["timestamp"],
                raw_data=raw_data_copy
            )
            db.add(info)
        
        db.commit()
        print(f"成功添加 {len(mock_data)} 条采集信息")
        
    except Exception as e:
        print(f"初始化数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_collected_data()
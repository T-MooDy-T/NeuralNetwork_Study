"""学生画像 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from ...database.connection import get_db
from ...database.models import User, Schedule, KnowledgeBase
from ...core.llm import QwenLLM

router = APIRouter(tags=["学生画像"])


@router.get("/profile/list", summary="获取学生列表")
async def get_student_list(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取学生列表（排除管理员）"""
    query = db.query(User).filter(User.role == "user", User.is_active == True)
    total = query.count()
    students = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for student in students:
        schedule_count = db.query(Schedule.id).filter(Schedule.user_id == student.id).count()
        result.append({
            "id": student.id,
            "username": student.username,
            "nickname": student.nickname,
            "email": student.email,
            "schedule_count": schedule_count,
            "created_at": student.created_at
        })
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/profile/{user_id}", summary="获取学生画像")
async def get_student_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取学生详细画像信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    return _build_student_profile(user, db)


def _build_student_profile(user: User, db: Session) -> Dict[str, Any]:
    """构建学生画像数据"""
    schedules = db.query(Schedule).filter(
        Schedule.user_id == user.id
    ).order_by(Schedule.start_time).all()
    
    # 分析活动时间
    activity_analysis = _analyze_activity_patterns(schedules)
    
    # 构建画像
    profile = {
        "basic_info": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname or user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login
        },
        "preferences": {
            "interests": _generate_interests(schedules),
            "favorite_courses": _extract_favorite_courses(schedules),
            "activity_types": _extract_activity_types(schedules)
        },
        "activity_patterns": activity_analysis,
        "learning_stats": {
            "total_schedules": len(schedules),
            "pending_schedules": len([s for s in schedules if s.status == "pending"]),
            "completed_schedules": len([s for s in schedules if s.status == "completed"]),
            "average_priority": _calculate_average_priority(schedules)
        },
        "recent_activities": _get_recent_activities(schedules)
    }
    
    return profile


def _analyze_activity_patterns(schedules: List[Schedule]) -> Dict[str, Any]:
    """分析活动时间模式"""
    if not schedules:
        return {
            "most_active_day": "无数据",
            "most_active_hour": "无数据",
            "morning_count": 0,
            "afternoon_count": 0,
            "evening_count": 0,
            "night_count": 0,
            "weekly_pattern": [0] * 7
        }
    
    hourly_counts = [0] * 24
    weekly_counts = [0] * 7  # 周一到周日
    
    for schedule in schedules:
        try:
            start_time = schedule.start_time
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace(" ", "T"))
            
            hour = start_time.hour
            weekday = start_time.weekday()
            
            hourly_counts[hour] += 1
            weekly_counts[weekday] += 1
        except:
            pass
    
    most_active_hour = hourly_counts.index(max(hourly_counts))
    most_active_day = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekly_counts.index(max(weekly_counts))]
    
    # 时间段统计
    morning_count = sum(hourly_counts[6:12])    # 6-12点
    afternoon_count = sum(hourly_counts[12:18])  # 12-18点
    evening_count = sum(hourly_counts[18:22])   # 18-22点
    night_count = sum(hourly_counts[22:24]) + sum(hourly_counts[0:6])  # 22-6点
    
    return {
        "most_active_day": most_active_day,
        "most_active_hour": f"{most_active_hour}:00",
        "morning_count": morning_count,
        "afternoon_count": afternoon_count,
        "evening_count": evening_count,
        "night_count": night_count,
        "weekly_pattern": weekly_counts
    }


def _generate_interests(schedules: List[Schedule]) -> List[str]:
    """从日程中提取兴趣爱好"""
    event_keywords = {
        "课程": ["课", "课程", "上课", "讲座", "讲座"],
        "体育": ["运动", "体育", "跑步", "篮球", "足球", "羽毛球", "游泳"],
        "学习": ["自习", "图书馆", "复习", "作业", "论文", "考试"],
        "社交": ["聚餐", "聚会", "会议", "活动", "社团"],
        "娱乐": ["电影", "游戏", "音乐会", "演出", "游玩"],
        "竞赛": ["比赛", "竞赛", "挑战杯", "建模"]
    }
    
    interests = []
    for schedule in schedules:
        event_name = schedule.event_name or ""
        for category, keywords in event_keywords.items():
            if any(keyword in event_name for keyword in keywords) and category not in interests:
                interests.append(category)
    
    if not interests:
        interests = ["学习", "社交"]
    
    return interests


def _extract_favorite_courses(schedules: List[Schedule]) -> List[str]:
    """提取偏好课程"""
    course_keywords = {
        "高等数学": ["高数", "数学", "微积分"],
        "英语": ["英语", "四级", "六级"],
        "计算机": ["计算机", "编程", "Python", "Java"],
        "物理": ["物理", "力学", "电磁"],
        "专业课": ["专业", "实验", "设计"]
    }
    
    courses = []
    for schedule in schedules:
        event_name = schedule.event_name or ""
        for course, keywords in course_keywords.items():
            if any(keyword in event_name for keyword in keywords) and course not in courses:
                courses.append(course)
    
    if not courses:
        courses = ["高等数学", "英语"]
    
    return courses[:5]


def _extract_activity_types(schedules: List[Schedule]) -> List[Dict[str, int]]:
    """提取活动类型分布"""
    type_counts = {
        "学习": 0,
        "社交": 0,
        "体育": 0,
        "娱乐": 0,
        "其他": 0
    }
    
    keywords = {
        "学习": ["课", "学习", "自习", "图书馆", "作业", "考试", "复习"],
        "社交": ["聚餐", "聚会", "会议", "社团"],
        "体育": ["运动", "体育", "篮球", "足球"],
        "娱乐": ["电影", "游戏", "游玩"]
    }
    
    for schedule in schedules:
        event_name = schedule.event_name or ""
        matched = False
        for activity_type, kw_list in keywords.items():
            if any(kw in event_name for kw in kw_list):
                type_counts[activity_type] += 1
                matched = True
                break
        if not matched:
            type_counts["其他"] += 1
    
    return [{"type": k, "count": v} for k, v in type_counts.items()]


def _calculate_average_priority(schedules: List[Schedule]) -> str:
    """计算平均优先级"""
    if not schedules:
        return "中等"
    
    priority_map = {"high": 3, "medium": 2, "low": 1}
    total = sum(priority_map.get(s.priority, 2) for s in schedules)
    avg = total / len(schedules)
    
    if avg >= 2.5:
        return "高"
    elif avg >= 1.5:
        return "中等"
    else:
        return "低"


def _get_recent_activities(schedules: List[Schedule]) -> List[Dict[str, Any]]:
    """获取最近活动"""
    recent = []
    sorted_schedules = sorted(schedules, key=lambda x: x.start_time or datetime.min, reverse=True)
    
    for schedule in sorted_schedules[:5]:
        try:
            start_time = schedule.start_time
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace(" ", "T"))
        except:
            start_time = None
        
        recent.append({
            "id": schedule.id,
            "event_name": schedule.event_name,
            "start_time": schedule.start_time,
            "location": schedule.location,
            "priority": schedule.priority,
            "status": schedule.status
        })
    
    return recent


@router.get("/profile/{user_id}/ai-analysis", summary="AI分析学生画像")
async def ai_analyze_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """使用AI分析学生画像并生成总结"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    profile = _build_student_profile(user, db)
    
    try:
        llm = QwenLLM()
        
        system_prompt = """你是一位校园AI助手，擅长分析学生画像并提供个性化建议。
        
        请根据学生画像数据，生成一份友好、专业的分析报告：
        1. 总结学生的主要特点
        2. 分析学习习惯和活动模式
        3. 提供个性化建议
        4. 使用emoji增加可读性
        5. 语言亲切自然
        """
        
        user_prompt = f"""学生画像数据：
        姓名：{profile['basic_info']['nickname']}
        
        兴趣爱好：{', '.join(profile['preferences']['interests'])}
        
        偏好课程：{', '.join(profile['preferences']['favorite_courses'])}
        
        活动时间分析：
        - 最活跃的一天：{profile['activity_patterns']['most_active_day']}
        - 最活跃的时段：{profile['activity_patterns']['most_active_hour']}
        - 上午活动：{profile['activity_patterns']['morning_count']}次
        - 下午活动：{profile['activity_patterns']['afternoon_count']}次
        - 晚上活动：{profile['activity_patterns']['evening_count']}次
        
        学习统计：
        - 总日程数：{profile['learning_stats']['total_schedules']}
        - 待完成：{profile['learning_stats']['pending_schedules']}
        - 已完成：{profile['learning_stats']['completed_schedules']}
        - 平均优先级：{profile['learning_stats']['average_priority']}
        
        请生成一份详细的学生画像分析报告。"""
        
        response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.7)
        
        try:
            kb_entry = KnowledgeBase(
                title=f"学生画像分析报告 - {profile['basic_info']['nickname']}",
                content=response,
                source_type="学生画像",
                category="AI分析",
                created_at=datetime.now()
            )
            db.add(kb_entry)
            db.commit()
            logger.info(f"学生画像分析报告已保存到知识库: {profile['basic_info']['nickname']}")
        except Exception as kb_error:
            logger.error(f"保存到知识库失败: {kb_error}")
        
        return {
            "success": True,
            "analysis": response,
            "profile": profile
        }
    
    except Exception as e:
        logger.error(f"AI分析失败: {e}")
        return {
            "success": False,
            "message": "AI分析失败，使用默认分析",
            "profile": profile
        }

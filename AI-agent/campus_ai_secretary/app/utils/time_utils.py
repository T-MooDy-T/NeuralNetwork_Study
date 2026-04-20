"""时间解析工具

支持自然语言时间解析，如：
- "明天下午3点"
- "下周一上午9点"
- "2024年1月15日 14:00"
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dateutil.relativedelta import relativedelta


# 中文数字映射
CN_NUMBERS = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "十一": 11, "十二": 12, "廿": 20, "卅": 30
}

# 星期映射
WEEKDAY_MAP = {
    "周一": 0, "星期一": 0, "一": 0,
    "周二": 1, "星期二": 1, "二": 1,
    "周三": 2, "星期三": 2, "三": 2,
    "周四": 3, "星期四": 3, "四": 3,
    "周五": 4, "星期五": 4, "五": 4,
    "周六": 5, "星期六": 5, "六": 5,
    "周日": 6, "星期日": 6, "星期天": 6, "日": 6, "天": 6
}

# 时间段映射
TIME_PERIOD = {
    "上午": (8, 12),
    "早上": (6, 9),
    "早": (6, 9),
    "中午": (12, 14),
    "下午": (14, 18),
    "傍晚": (17, 19),
    "晚上": (18, 22),
    "晚": (18, 22),
    "深夜": (22, 2),
    "凌晨": (0, 5),
}


def cn_to_number(text: str) -> int:
    """将中文数字转换为阿拉伯数字"""
    if text.isdigit():
        return int(text)
    
    result = 0
    for char in text:
        if char in CN_NUMBERS:
            result += CN_NUMBERS[char]
    return result


def parse_relative_date(text: str, base: datetime) -> Tuple[datetime, bool]:
    """解析相对日期"""
    text = text.strip()
    modified = False
    
    # 今天
    if "今天" in text or "今日" in text:
        base = base.replace(hour=0, minute=0, second=0, microsecond=0)
        text = text.replace("今天", "").replace("今日", "")
        modified = True
    
    # 明天
    elif "明天" in text or "明日" in text:
        base = (base + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        text = text.replace("明天", "").replace("明日", "")
        modified = True
    
    # 后天
    elif "后天" in text:
        base = (base + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        text = text.replace("后天", "")
        modified = True
    
    # 大后天
    elif "大后天" in text:
        base = (base + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        text = text.replace("大后天", "")
        modified = True
    
    # 昨天
    elif "昨天" in text:
        base = (base - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        text = text.replace("昨天", "")
        modified = True
    
    # 下周X
    week_match = re.search(r"下(?:周|星期)([一二三四五六日天])", text)
    if week_match:
        weekday = WEEKDAY_MAP.get(f"周{week_match.group(1)}", WEEKDAY_MAP.get(week_match.group(1)))
        current_weekday = base.weekday()
        days_ahead = (7 - current_weekday) + weekday  # 下周
        base = (base + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        text = re.sub(r"下(?:周|星期)[一二三四五六日天]", "", text)
        modified = True
    
    # 本周X
    week_match = re.search(r"本(?:周|星期)([一二三四五六日天])", text)
    if week_match:
        weekday = WEEKDAY_MAP.get(f"周{week_match.group(1)}", WEEKDAY_MAP.get(week_match.group(1)))
        current_weekday = base.weekday()
        if weekday >= current_weekday:
            days_ahead = weekday - current_weekday
        else:
            days_ahead = 7 - current_weekday + weekday  # 本周已过去，算下周
        base = (base + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        text = re.sub(r"本(?:周|星期)[一二三四五六日天]", "", text)
        modified = True
    
    return base, modified, text


def parse_absolute_date(text: str, base: datetime) -> Tuple[datetime, str]:
    """解析绝对日期"""
    # 2024年1月15日
    match = re.search(r"(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日号]?", text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        base = datetime(year, month, day)
        text = re.sub(r"\d{4}[年\-/]\d{1,2}[月\-/]\d{1,2}[日号]?", "", text)
        return base, text
    
    # 1月15日（默认今年）
    match = re.search(r"(\d{1,2})[月\-/](\d{1,2})[日号]?", text)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        year = base.year
        # 如果月份小于当前月，可能是明年
        if month < base.month:
            year += 1
        base = datetime(year, month, day)
        text = re.sub(r"\d{1,2}[月\-/]\d{1,2}[日号]?", "", text)
        return base, text
    
    return base, text


def parse_time_period(text: str) -> Tuple[Optional[int], str]:
    """解析时间段"""
    for period, (start_hour, end_hour) in TIME_PERIOD.items():
        if period in text:
            text = text.replace(period, "")
            return start_hour, text
    return None, text


def parse_specific_time(text: str) -> Tuple[Optional[int], Optional[int], str]:
    """解析具体时间"""
    # 14:30 或 14点30分
    match = re.search(r"(\d{1,2})[:点时](\d{0,2})?[分]?", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        text = re.sub(r"\d{1,2}[:点时]\d{0,2}[分]?", "", text)
        return hour, minute, text
    
    # 下午3点（只有小时）
    match = re.search(r"(\d{1,2})[点时]", text)
    if match:
        hour = int(match.group(1))
        text = re.sub(r"\d{1,2}[点时]", "", text)
        return hour, 0, text
    
    return None, None, text


def parse_time(time_str: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    解析自然语言时间为标准datetime对象
    
    Args:
        time_str: 时间字符串，如 "明天下午3点"
        base_time: 基准时间（默认当前时间）
    
    Returns:
        解析后的datetime对象，解析失败返回None
    """
    if not time_str:
        return None
    
    base = base_time or datetime.now()
    text = time_str.strip()
    
    # 1. 解析相对日期
    base, modified, text = parse_relative_date(text, base)
    
    # 2. 解析绝对日期
    if not modified:
        base, text = parse_absolute_date(text, base)
    
    # 3. 解析时间段（上午、下午等）
    period_hour, text = parse_time_period(text)
    
    # 4. 解析具体时间
    hour, minute, text = parse_specific_time(text)
    
    # 组合时间
    if hour is not None:
        # 如果有时间段，调整小时
        if period_hour is not None:
            # 下午3点 = 15点
            if period_hour >= 12 and hour < 12:
                hour += 12
            # 上午12点 = 12点（不调整）
        
        return base.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    elif period_hour is not None:
        # 只有时间段，默认取时间段开始
        return base.replace(hour=period_hour, minute=0, second=0, microsecond=0)
    
    elif modified:
        # 只有日期，默认早上9点
        return base.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # 无法解析
    return None


def get_current_time(timezone: str = "Asia/Shanghai") -> datetime:
    """获取当前时间（北京时间）"""
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(timezone))


def format_time_display(dt: datetime) -> str:
    """格式化时间为友好显示"""
    now = datetime.now()
    
    if dt.date() == now.date():
        return f"今天 {dt.strftime('%H:%M')}"
    elif dt.date() == (now + timedelta(days=1)).date():
        return f"明天 {dt.strftime('%H:%M')}"
    elif dt.date() == (now + timedelta(days=2)).date():
        return f"后天 {dt.strftime('%H:%M')}"
    else:
        return dt.strftime("%Y年%m月%d日 %H:%M")


def parse_remind_offset(offset_str: str) -> timedelta:
    """解析提醒时间偏移
    
    支持: 1d (一天前), 3h (三小时前), 30m (30分钟前)
    """
    match = re.match(r"(\d+)([dhm])", offset_str)
    if not match:
        return timedelta(hours=1)  # 默认1小时
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == "d":
        return timedelta(days=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "m":
        return timedelta(minutes=value)
    
    return timedelta(hours=1)
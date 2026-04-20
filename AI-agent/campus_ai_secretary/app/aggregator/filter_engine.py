from loguru import logger
from typing import List, Dict

class FilterEngine:
    def __init__(self):
        self.keywords = {
            'important': ['必须', '务必', '紧急', '截止', '考试', '选课', '通知', '报名', '提交'],
            'event': ['会议', '活动', '聚餐', '讲座', '比赛', '竞赛', '报名', '参加'],
            'academic': ['作业', '论文', '报告', '答辩', '课程', '上课', '选课', '成绩'],
            'social': ['聚会', '团建', '生日', '聚餐', '晚会', '联谊'],
            'campus': ['图书馆', '食堂', '宿舍', '校医院', '体育馆']
        }
        logger.info("Filter engine initialized")
    
    def classify(self, info: Dict) -> Dict:
        content = info['content']
        
        categories = []
        priority = 'normal'
        
        for cat, keys in self.keywords.items():
            for key in keys:
                if key in content:
                    categories.append(cat)
                    if cat == 'important':
                        priority = 'high'
                    elif priority == 'normal' and cat == 'event':
                        priority = 'medium'
                    break
        
        if not categories:
            categories.append('other')
        
        info['categories'] = categories
        info['priority'] = priority
        
        return info
    
    def filter_and_rank(self, info_list: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        classified = [self.classify(info) for info in info_list]
        
        filtered = [info for info in classified if info['priority'] != 'low']
        
        if user_preferences:
            filtered = self._apply_preferences(filtered, user_preferences)
        
        ranked = sorted(filtered, key=lambda x: self._get_rank_score(x), reverse=True)
        
        return ranked
    
    def _apply_preferences(self, info_list: List[Dict], preferences: Dict) -> List[Dict]:
        filtered = []
        for info in info_list:
            if 'exclude_categories' in preferences:
                if any(cat in preferences['exclude_categories'] for cat in info['categories']):
                    continue
            if 'include_categories' in preferences:
                if not any(cat in preferences['include_categories'] for cat in info['categories']):
                    continue
            filtered.append(info)
        return filtered
    
    def _get_rank_score(self, info: Dict) -> int:
        score = 0
        
        if info['priority'] == 'high':
            score += 10
        elif info['priority'] == 'medium':
            score += 5
        
        if 'important' in info['categories']:
            score += 8
        if 'event' in info['categories']:
            score += 5
        if 'academic' in info['categories']:
            score += 3
        
        return score
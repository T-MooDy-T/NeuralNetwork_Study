import requests
from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict
import time

class WeChatOfficialCollector:
    def __init__(self):
        self.accounts = []
        logger.info("WeChat Official collector initialized")
    
    def add_account(self, account_id: str, account_name: str):
        self.accounts.append({
            'id': account_id,
            'name': account_name,
            'last_fetch_time': 0
        })
        logger.info(f"Subscribed to official account: {account_name}")
    
    def fetch_articles(self, account_id: str = None) -> List[Dict]:
        articles = []
        
        target_accounts = self.accounts if not account_id else \
            [a for a in self.accounts if a['id'] == account_id]
        
        for account in target_accounts:
            try:
                arts = self._fetch_articles(account['id'])
                articles.extend(arts)
                account['last_fetch_time'] = int(time.time())
            except Exception as e:
                logger.error(f"Failed to fetch articles from {account['name']}: {e}")
        
        return articles
    
    def _fetch_articles(self, account_id: str) -> List[Dict]:
        account_name = next(a['name'] for a in self.accounts if a['id'] == account_id)
        
        return [
            {
                'account_id': account_id,
                'account_name': account_name,
                'title': '关于举办2024年校园科技节的通知',
                'url': 'https://mp.weixin.qq.com/s/example123',
                'summary': '校园科技节将于下周五（10月20日）在体育馆举行，欢迎同学们积极参与各类科技竞赛和展览活动',
                'publish_time': int(time.time()),
                'type': 'article'
            },
            {
                'account_id': account_id,
                'account_name': account_name,
                'title': '图书馆新增电子资源数据库通知',
                'url': 'https://mp.weixin.qq.com/s/example456',
                'summary': '图书馆新增CNKI、万方等多个数据库的访问权限，同学们可以在校内免费使用',
                'publish_time': int(time.time()) - 86400,
                'type': 'article'
            },
            {
                'account_id': account_id,
                'account_name': account_name,
                'title': '大学生创业大赛报名开始',
                'url': 'https://mp.weixin.qq.com/s/example789',
                'summary': '第八届大学生创业大赛现已开放报名，截止日期11月1日，丰厚奖金等你拿',
                'publish_time': int(time.time()) - 172800,
                'type': 'article'
            }
        ]
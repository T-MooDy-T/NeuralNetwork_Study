from loguru import logger
from typing import List, Dict, Any
from datetime import datetime

class InfoAggregator:
    def __init__(self):
        self.collectors = {}
        logger.info("Info aggregator initialized")
    
    def register_collector(self, name: str, collector):
        self.collectors[name] = collector
        logger.info(f"Registered collector: {name}")
    
    def collect_all(self) -> List[Dict]:
        all_info = []
        
        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, 'fetch_messages'):
                    msgs = collector.fetch_messages()
                    all_info.extend(msgs)
                elif hasattr(collector, 'fetch_articles'):
                    articles = collector.fetch_articles()
                    all_info.extend(articles)
            except Exception as e:
                logger.error(f"Collector {name} failed: {e}")
        
        return self._normalize_info(all_info)
    
    def _normalize_info(self, raw_info: List[Dict]) -> List[Dict]:
        normalized = []
        
        for info in raw_info:
            item = {
                'id': info.get('id', str(hash(str(info)))),
                'source': info.get('group_name') or info.get('chat_name') or info.get('account_name'),
                'source_type': self._detect_source_type(info),
                'sender': info.get('sender', 'unknown'),
                'content': info.get('content') or info.get('title') or info.get('summary'),
                'url': info.get('url'),
                'timestamp': info.get('timestamp', int(datetime.now().timestamp())),
                'type': info.get('type', 'unknown'),
                'raw_data': info
            }
            normalized.append(item)
        
        return sorted(normalized, key=lambda x: x['timestamp'], reverse=True)
    
    def _detect_source_type(self, info: Dict) -> str:
        if 'group_id' in info:
            return 'qq_group'
        elif 'chat_id' in info:
            return 'wechat_chat'
        elif 'account_id' in info:
            return 'wechat_official'
        return 'unknown'
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from loguru import logger

from ...aggregator.info_aggregator import InfoAggregator
from ...aggregator.filter_engine import FilterEngine
from ...core.auth import get_current_user, TokenData

router = APIRouter(prefix="/collector", tags=["信息采集"])

aggregator = InfoAggregator()
filter_engine = FilterEngine()

@router.get("/sources", summary="获取采集源列表")
async def get_sources(current_user: TokenData = Depends(get_current_user)):
    return {
        "sources": [
            {"id": "qq", "name": "QQ群", "status": "connected"},
            {"id": "wechat", "name": "微信群", "status": "connected"},
            {"id": "official", "name": "公众号", "status": "connected"}
        ]
    }

@router.post("/qq/groups", summary="添加QQ群监控")
async def add_qq_group(
    group_id: str, 
    group_name: str,
    current_user: TokenData = Depends(get_current_user)
):
    from ...data_collector.qq_collector import QQCollector
    
    if 'qq' not in aggregator.collectors:
        aggregator.register_collector('qq', QQCollector())
    
    aggregator.collectors['qq'].add_group(group_id, group_name)
    return {"message": f"Added QQ group monitor: {group_name}"}

@router.post("/wechat/chats", summary="添加微信群监控")
async def add_wechat_chat(
    chat_id: str, 
    chat_name: str,
    current_user: TokenData = Depends(get_current_user)
):
    from ...data_collector.wechat_collector import WeChatCollector
    
    if 'wechat' not in aggregator.collectors:
        aggregator.register_collector('wechat', WeChatCollector())
    
    aggregator.collectors['wechat'].add_chat(chat_id, chat_name)
    return {"message": f"Added WeChat chat monitor: {chat_name}"}

@router.post("/official/accounts", summary="订阅公众号")
async def add_official_account(
    account_id: str, 
    account_name: str,
    current_user: TokenData = Depends(get_current_user)
):
    from ...data_collector.wechat_official import WeChatOfficialCollector
    
    if 'official' not in aggregator.collectors:
        aggregator.register_collector('official', WeChatOfficialCollector())
    
    aggregator.collectors['official'].add_account(account_id, account_name)
    return {"message": f"Subscribed to official account: {account_name}"}

@router.get("/info", summary="获取聚合信息")
async def get_aggregated_info(
    limit: int = 20,
    priority: str = None,
    current_user: TokenData = Depends(get_current_user)
):
    try:
        all_info = aggregator.collect_all()
        filtered = filter_engine.filter_and_rank(all_info)
        
        if priority:
            filtered = [info for info in filtered if info['priority'] == priority]
        
        return {
            "total": len(filtered),
            "items": filtered[:limit]
        }
    except Exception as e:
        logger.error(f"Failed to get aggregated info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get info")


@router.post("/qq/welcome", summary="QQbot发送欢迎消息")
async def send_qq_welcome(
    group_id: str = None,
    current_user: TokenData = Depends(get_current_user)
):
    """向QQ群发送欢迎消息"""
    try:
        from ...data_collector.qq_collector import QQCollector
        
        if 'qq' not in aggregator.collectors:
            aggregator.register_collector('qq', QQCollector())
        
        qq_collector = aggregator.collectors['qq']
        
        if group_id:
            result = qq_collector.send_welcome_message(group_id)
            return {"message": f"欢迎消息发送{'成功' if result else '失败'}", "group_id": group_id}
        else:
            qq_collector.broadcast_welcome()
            return {"message": "已向所有监控群发送欢迎消息"}
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")
        raise HTTPException(status_code=500, detail="发送失败")
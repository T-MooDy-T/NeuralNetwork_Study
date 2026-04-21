"""智能问答 API"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from loguru import logger

from ...models.schedule import QARequest, QAResponse, ScheduleCreate
from ...dependencies import get_rag_engine, get_llm

router = APIRouter()


@router.post("/ask", response_model=QAResponse, summary="智能问答")
async def ask_question(question: str, user_id: str = "default", context: Optional[str] = None):
    """基于知识库回答用户问题"""
    try:
        rag = get_rag_engine()
        llm = get_llm()
        
        # 1. 检索相关知识
        search_results = rag.search(question, top_k=3)
        
        # 2. 构建上下文
        kb_context = None
        if search_results:
            kb_context = "\n\n".join([
                f"[来源：{r['metadata'].get('source_type', 'unknown')}]\n{r['content']}"
                for r in search_results
            ])
        
        # 3. 生成回答
        response_data = llm.answer_question(question, kb_context)
        
        # 4. 构建响应
        response = QAResponse(
            answer=response_data["answer"],
            sources=search_results,
            confidence=response_data["confidence"],
            can_create_schedule=False
        )
        
        logger.info(f"API: 问答 - 用户：{user_id}, 问题：{question[:30]}..., 置信度：{response.confidence}")
        return response
    except Exception as e:
        logger.exception(f"问答失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kb/add", summary="添加知识库文档")
async def add_knowledge_document(content: str, source_type: str = "manual", user_id: str = "default"):
    """添加文档到知识库"""
    try:
        rag = get_rag_engine()
        
        metadata = {
            "source_type": source_type,
            "user_id": user_id,
            "created_at": "now"
        }
        
        rag.add_document(content, metadata)
        
        logger.info(f"API: 添加知识库文档 - 类型：{source_type}")
        return {"success": True, "message": "文档已添加到知识库"}
    except Exception as e:
        logger.exception(f"添加文档失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kb/stats", summary="获取知识库统计")
async def get_knowledge_stats():
    """获取知识库统计信息"""
    rag = get_rag_engine()
    stats = rag.get_knowledge_stats()
    return stats


@router.post("/kb/batch-add", summary="批量添加知识库文档")
async def batch_add_documents(documents: list):
    """批量添加文档到知识库
    
    documents: [{"content": "...", "metadata": {...}}, ...]
    """
    try:
        rag = get_rag_engine()
        rag.add_knowledge_base(documents)
        
        logger.info(f"API: 批量添加 {len(documents)} 篇文档到知识库")
        return {"success": True, "count": len(documents)}
    except Exception as e:
        logger.exception(f"批量添加文档失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))

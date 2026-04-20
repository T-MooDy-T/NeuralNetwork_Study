"""RAG 检索引擎

基于 Qdrant 向量数据库实现语义检索
支持内存模式（本地测试）和服务模式
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("qdrant-client 未安装，RAG 功能将使用简化模式")

from .llm import QwenLLM


class RAGEngine:
    """RAG 检索引擎"""
    
    def __init__(self, 
                 collection_name: Optional[str] = None,
                 use_memory: bool = True,
                 llm: Optional[QwenLLM] = None):
        """初始化 RAG 引擎
        
        Args:
            collection_name: 集合名称
            use_memory: 是否使用内存模式（本地测试）
            llm: LLM 实例，用于生成嵌入向量
        """
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "campus_ai_kb")
        self.use_memory = use_memory
        self.llm = llm or QwenLLM()
        
        # 简化的内存存储（用于 Demo）
        self.memory_store: List[Dict[str, Any]] = []
        
        if QDRANT_AVAILABLE and not use_memory:
            self._init_qdrant()
        else:
            logger.info("RAG 引擎使用内存模式")
            self.qdrant = None
    
    def _init_qdrant(self):
        """初始化 Qdrant 客户端"""
        mode = os.getenv("QDRANT_MODE", "memory")
        
        if mode == "memory":
            self.qdrant = QdrantClient(":memory:")
        else:
            host = os.getenv("QDRANT_HOST", "localhost")
            port = int(os.getenv("QDRANT_PORT", "6333"))
            self.qdrant = QdrantClient(host=host, port=port)
        
        self._create_collection()
        logger.info(f"Qdrant 初始化完成，集合：{self.collection_name}")
    
    def _create_collection(self):
        """创建集合"""
        if not self.qdrant:
            return
        
        try:
            collections = self.qdrant.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # text-embedding-3-small 维度
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"创建集合：{self.collection_name}")
        except Exception as e:
            logger.error(f"创建集合失败：{e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量
        
        注意：这里使用简化的方法，实际应该调用嵌入模型
        Demo 中使用千问的文本表示替代
        """
        # TODO: 接入真实的嵌入模型（如 text-embedding-3-small 或 M3E）
        # 这里使用简化方案：返回一个固定维度的向量用于 Demo
        
        import hashlib
        import numpy as np
        
        # 使用 hash 生成伪向量（仅用于 Demo 测试）
        hash_bytes = hashlib.sha256(text.encode()).digest()
        vector = np.frombuffer(hash_bytes, dtype=np.uint8).astype(float) / 255.0
        
        # 扩展到 1536 维
        vector = np.tile(vector, 48)[:1536].tolist()
        
        return vector
    
    def add_document(self, content: str, metadata: Optional[Dict] = None):
        """添加文档到知识库
        
        Args:
            content: 文档内容
            metadata: 元数据（source_type, publish_time, priority 等）
        """
        doc_id = str(uuid.uuid4())
        if metadata and metadata.get("chunk_id"):
            doc_id = metadata["chunk_id"]
        
        if self.qdrant:
            try:
                embedding = self.get_embedding(content)
                point = PointStruct(
                    id=hash(doc_id) % (2**63),  # Qdrant 需要整数 ID
                    vector=embedding,
                    payload={
                        "content": content,
                        "chunk_id": doc_id,
                        **(metadata or {})
                    }
                )
                self.qdrant.upsert(
                    collection_name=self.collection_name,
                    points=[point]
                )
                logger.info(f"添加文档到知识库：{doc_id[:8]}...")
            except Exception as e:
                logger.error(f"添加文档失败：{e}")
        else:
            # 内存模式
            self.memory_store.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata or {},
                "embedding": self.get_embedding(content)
            })
            logger.info(f"添加文档到内存知识库：{doc_id[:8]}...")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            相关文档列表
        """
        if self.qdrant:
            try:
                query_embedding = self.get_embedding(query)
                results = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    with_payload=True
                )
                
                return [
                    {
                        "content": result.payload.get("content"),
                        "metadata": {k: v for k, v in result.payload.items() 
                                   if k not in ["content"]},
                        "score": result.score
                    }
                    for result in results
                ]
            except Exception as e:
                logger.error(f"检索失败：{e}")
                return []
        else:
            # 内存模式：简单相似度计算
            query_embedding = self.get_embedding(query)
            import numpy as np
            
            scored_docs = []
            for doc in self.memory_store:
                # 余弦相似度
                similarity = np.dot(query_embedding, doc["embedding"]) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc["embedding"])
                )
                scored_docs.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": float(similarity)
                })
            
            # 排序返回 top_k
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            return scored_docs[:top_k]
    
    def add_knowledge_base(self, documents: List[Dict[str, Any]]):
        """批量添加知识库文档
        
        Args:
            documents: 文档列表，每个文档包含 content 和 metadata
        """
        for doc in documents:
            self.add_document(doc["content"], doc.get("metadata"))
        
        logger.info(f"批量添加 {len(documents)} 篇文档到知识库")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        if self.qdrant:
            try:
                info = self.qdrant.get_collection(self.collection_name)
                return {
                    "document_count": info.points_count,
                    "collection": self.collection_name
                }
            except:
                return {"document_count": 0, "collection": self.collection_name}
        else:
            return {
                "document_count": len(self.memory_store),
                "collection": f"{self.collection_name} (memory)"
            }

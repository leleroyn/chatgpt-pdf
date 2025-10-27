import os
import json
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from dotenv import load_dotenv
load_dotenv()

class VectorDBService:
    """向量数据库服务类"""
    
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.embedding_model_path = os.getenv("EMBEDDING_MODEL_PATH")
        
        # 初始化向量数据库客户端
        self.qdrant_client = QdrantClient(url=self.qdrant_url)
        
        # 固定知识库名称
        self.collection_name = "Simple_KB"
        
        # 固定向量维度为768
        self.vector_size = 768
        
        # 加载嵌入模型
        self._load_embedding_model()
        
        # 确保集合存在
        self._ensure_collection_exists()
    
    def _load_embedding_model(self):
        """加载嵌入模型（单例模式）"""
        # 检查是否已经加载过
        if hasattr(self, '_model_loaded') and self._model_loaded:
            return
            
        try:
            if not self.embedding_model_path:
                raise ValueError("EMBEDDING_MODEL_PATH环境变量未设置")
            
            # 使用transformers加载预训练模型
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            print(f"正在加载嵌入模型: {self.embedding_model_path}")
            
            # 检查模型路径是否存在
            if not os.path.exists(self.embedding_model_path):
                raise FileNotFoundError(f"嵌入模型路径不存在: {self.embedding_model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_path, trust_remote_code=True)
            self.embedding_model = AutoModel.from_pretrained(self.embedding_model_path, trust_remote_code=True)
            
            # 设置为评估模式
            self.embedding_model.eval()
            
            # 标记为已加载
            self._model_loaded = True
            print("嵌入模型加载成功")
            
        except Exception as e:
            print(f"加载嵌入模型失败: {e}")
            raise e
    
    def _ensure_collection_exists(self):
        """确保向量数据库集合存在"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                # 创建新集合
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                print(f"创建集合: {self.collection_name}, 向量维度: {self.vector_size}")
            else:
                # 检查现有集合的维度是否匹配
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                existing_dim = collection_info.config.params.vectors.size
                
                if existing_dim != self.vector_size:
                    print(f"集合维度不匹配（现有: {existing_dim}, 需要: {self.vector_size}），删除旧集合并重新创建")
                    # 删除旧集合
                    self.qdrant_client.delete_collection(self.collection_name)
                    # 创建新集合
                    self.qdrant_client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                    )
                    print(f"重新创建集合: {self.collection_name}, 向量维度: {self.vector_size}")
                    
        except Exception as e:
            print(f"确保集合存在时出错: {e}")
            raise e
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入模型的维度"""
        return self.vector_size
    
    def encode_text(self, text: str) -> List[float]:
        """将文本编码为向量"""
        import torch
        
        # 对文本进行编码
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
            # 取最后一层隐藏状态的平均值作为句子嵌入
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        
        return embeddings.tolist()
    
    def store_document_chunks(self, document_id: str, text_chunks: List[str], metadata: Dict = None) -> int:
        """存储文档分块到向量数据库"""
        if not text_chunks:
            return 0
        
        points = []
        for i, chunk in enumerate(text_chunks):
            # 生成嵌入向量
            embedding = self.encode_text(chunk)
            
            # 创建点结构
            payload = {
                "text": chunk,
                "chunk_index": i,
                "document_id": document_id,
                "total_chunks": len(text_chunks)
            }
            
            # 添加额外元数据
            if metadata:
                payload.update(metadata)
            
            # 生成有效的Qdrant ID（使用UUID）
            import uuid
            point_id = uuid.uuid4().int % (2**63 - 1)
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
            points.append(point)
        
        # 批量插入向量数据库
        if points:
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
        
        return len(points)
    
    def search_similar_chunks(self, query: str, top_k: int = 5, document_id: str = None) -> List[Dict]:
        """搜索相似的文本块"""
        # 生成查询向量
        query_embedding = self.encode_text(query)
        
        # 构建过滤器
        filter_condition = None
        if document_id:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        
        # 搜索相似向量
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filter_condition,
            limit=top_k
        )
        
        # 提取搜索结果
        results = []
        for result in search_results:
            results.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "chunk_index": result.payload.get("chunk_index", 0),
                "document_id": result.payload.get("document_id", ""),
                "metadata": {k: v for k, v in result.payload.items() 
                           if k not in ["text", "chunk_index", "document_id", "total_chunks"]}
            })
        
        return results
    
    def delete_document(self, document_id: str) -> bool:
        """删除指定文档的所有分块"""
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            return True
        except Exception as e:
            print(f"删除文档时出错: {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """获取集合信息"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "name": collection_info.name,
                "status": collection_info.status,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            return {"error": str(e)}
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """将文本分块"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # 移动起始位置，考虑重叠
            start = end - overlap
            
            # 如果剩余文本不足一个块的大小，直接取剩余所有文本
            if start + chunk_size >= len(text):
                chunks.append(text[start:])
                break
        
        return chunks
import os
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class VectorDBService:
    def __init__(self):
        """初始化向量数据库服务"""
        self.qdrant_url = "http://192.168.1.252:6333/"
        self.collection_name = "company"
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL_PATH", "text2vec-base-multilingual")
        
        # 初始化Qdrant客户端
        self.client = QdrantClient(url=self.qdrant_url)
        
        # 初始化嵌入模型
        self.tokenizer = None
        self.model = None
        self._init_embedding_model()
        
        # 确保集合存在
        self._ensure_collection()
    
    def _init_embedding_model(self):
        """初始化嵌入模型"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
            self.model = AutoModel.from_pretrained(self.embedding_model_name, trust_remote_code=True)
            print(f"嵌入模型加载成功: {self.embedding_model_name}")
        except Exception as e:
            print(f"加载嵌入模型失败: {e}")
            raise
    
    def _ensure_collection(self):
        """确保集合存在，如果不存在则创建"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # 创建新的集合，使用384维向量（text2vec-base-multilingual的实际维度）
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"集合 {self.collection_name} 创建成功")
            else:
                print(f"集合 {self.collection_name} 已存在")
        except Exception as e:
            print(f"确保集合存在失败: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的嵌入向量"""
        if not text or not text.strip():
            return [0.0] * 384
        
        try:
            # 对文本进行编码
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # 获取嵌入
            with torch.no_grad():
                outputs = self.model(**inputs)
                # 使用平均池化获取句子嵌入
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
                
            # 转换为列表
            embedding_list = embeddings.tolist()
            
            # text2vec-base-multilingual 模型输出384维向量
            # 确保维度正确
            if len(embedding_list) != 384:
                print(f"警告: 嵌入向量维度为 {len(embedding_list)}，期望384维")
                # 如果维度不匹配，截断或填充到384维
                if len(embedding_list) > 384:
                    embedding_list = embedding_list[:384]
                else:
                    embedding_list.extend([0.0] * (384 - len(embedding_list)))
            
            return embedding_list
            
        except Exception as e:
            print(f"获取嵌入失败: {e}")
            # 返回零向量作为fallback
            return [0.0] * 384
    
    def add_companies(self, companies: List[str]) -> int:
        """添加公司名到向量库"""
        if not companies:
            return 0
        
        try:
            # 获取当前集合中的最大ID
            existing_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=1,
                with_payload=False,
                with_vectors=False
            )[0]
            
            start_id = 1
            if existing_points:
                max_id = max([point.id for point in existing_points])
                start_id = max_id + 1
            
            # 分批处理，避免Payload过大
            batch_size = 100
            total_added = 0
            
            for batch_start in range(0, len(companies), batch_size):
                batch_end = min(batch_start + batch_size, len(companies))
                batch_companies = companies[batch_start:batch_end]
                
                points = []
                
                # 为当前批次的公司创建向量点
                for i, company in enumerate(batch_companies):
                    if not company or not company.strip():
                        continue
                        
                    company = company.strip()
                    embedding = self.get_embedding(company)
                    
                    point = PointStruct(
                        id=start_id + batch_start + i,
                        vector=embedding,
                        payload={
                            "company_name": company,
                            "text": company
                        }
                    )
                    points.append(point)
                
                if points:
                    # 批量插入当前批次
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    total_added += len(points)
                    print(f"批次 {batch_start//batch_size + 1}: 成功添加 {len(points)} 个公司")
            
            if total_added > 0:
                print(f"总计成功添加 {total_added} 个公司到向量库")
            
            return total_added
                
        except Exception as e:
            print(f"添加公司到向量库失败: {e}")
            raise
    
    def search_companies(self, query: str, limit: int = 10) -> List[dict]:
        """搜索相似的公司名"""
        try:
            query_embedding = self.get_embedding(query)
            
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            
            results = []
            for result in search_results:
                results.append({
                    "company_name": result.payload.get("company_name", ""),
                    "score": result.score,
                    "id": result.id
                })
            
            return results
            
        except Exception as e:
            print(f"搜索公司失败: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """获取集合信息"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status
            }
        except Exception as e:
            print(f"获取集合信息失败: {e}")
            return {"points_count": 0, "vectors_count": 0, "status": "unknown"}
    
    def verify_data_added(self, company_name: str) -> bool:
        """验证数据是否成功添加到向量库"""
        try:
            # 搜索刚添加的公司
            results = self.search_companies(company_name, limit=5)
            
            if results:
                print(f"验证成功: 找到 {len(results)} 个匹配结果")
                for result in results:
                    print(f"  - {result['company_name']} (相似度: {result['score']:.4f})")
                return True
            else:
                print("验证失败: 未找到匹配结果")
                return False
        except Exception as e:
            print(f"验证数据失败: {e}")
            return False
import os
import re
from typing import List, Optional
import Levenshtein
import heapq


class CompanyMatchService:
    def __init__(self):
        """初始化服务"""
        # 存储公司名列表用于Levenshtein距离计算
        self.companies = []
    
    def add_companies(self, companies: List[str]) -> int:
        """添加公司名到本地列表"""
        if not companies:
            return 0
        
        try:
            # 清空现有列表
            self.companies.clear()
            
            # 添加新公司
            total_added = 0
            for company in companies:
                if company and company.strip():
                    company_clean = company.strip()
                    self.companies.append(company_clean)
                    total_added += 1
            
            print(f"总计成功添加 {total_added} 个公司到本地列表")
            return total_added
                
        except Exception as e:
            print(f"添加公司失败: {e}")
            raise
    
    def search_companies(self, query: str, limit: int = 10) -> List[dict]:
        """使用Levenshtein距离搜索相似的公司名（全量匹配版本）"""
        try:
            if not query or not query.strip():
                return []
            
            query = query.strip()
            
            # 使用堆（优先队列）来维护距离最小的前limit个结果
            heap = []  # 最大堆，存储(-distance, company)对
            
            # 对所有公司名进行全量匹配
            for company in self.companies:
                # 计算编辑距离
                distance = Levenshtein.distance(query, company)
                
                # 计算相似度分数
                max_len = max(len(query), len(company))
                if max_len == 0:
                    score = 1.0
                else:
                    score = 1.0 - (distance / max_len)
                
                # 使用堆来维护前limit个最小距离的结果
                if len(heap) < limit:
                    heapq.heappush(heap, (-distance, company, score))
                else:
                    # 如果当前距离比堆中最大距离小，替换
                    if distance < -heap[0][0]:
                        heapq.heappushpop(heap, (-distance, company, score))
            
            # 从堆中提取结果并排序
            results = []
            while heap:
                neg_distance, company, score = heapq.heappop(heap)
                results.append({
                    "company_name": company,
                    "score": score,
                    "distance": -neg_distance
                })
            
            # 按距离升序排序（距离最小的在前）
            results.sort(key=lambda x: x["distance"])
            
            return results
            
        except Exception as e:
            print(f"搜索公司失败: {e}")
            return []   

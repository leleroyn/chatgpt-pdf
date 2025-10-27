import os
from io import BytesIO
from time import time

import streamlit as st
from PIL import Image

from service.OcrService import OcrService
from service.VectorDBService import VectorDBService
from service.vllm_inference import text_inference_with_llm


class SmartQAKB:
    def __init__(self):
        self.ocr_service = OcrService()
        self.vector_db_service = VectorDBService()
        self.kb_name = "Simple_KB"
    
    def initialize_knowledge_base(self):
        """初始化知识库"""
        try:
            # 检查知识库是否存在
            collections = self.vector_db_service.qdrant_client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.kb_name in collection_names:
                # 尝试搜索来检查集合是否有内容
                try:
                    search_results = self.vector_db_service.search_similar_chunks("test", top_k=1)
                    if search_results:
                        st.success(f"知识库 '{self.kb_name}' 已加载，包含内容")
                    else:
                        st.info(f"知识库 '{self.kb_name}' 已加载（当前为空，请上传文档构建知识库）")
                except Exception:
                    st.info(f"知识库 '{self.kb_name}' 已加载（当前为空，请上传文档构建知识库）")
            else:
                # 知识库不存在，创建新知识库
                st.info(f"知识库 '{self.kb_name}' 不存在，将创建新知识库")
                self.vector_db_service._ensure_collection_exists()
                st.success(f"知识库 '{self.kb_name}' 创建成功（当前为空）")
                
            return True
        except Exception as e:
            st.error(f"初始化知识库失败: {str(e)}")
            return False
    
    def clear_knowledge_base(self):
        """清空知识库"""
        try:
            collections = self.vector_db_service.qdrant_client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.kb_name in collection_names:
                self.vector_db_service.qdrant_client.delete_collection(self.kb_name)
                st.success(f"知识库 '{self.kb_name}' 已清空")
            else:
                st.info(f"知识库 '{self.kb_name}' 不存在，无需清空")
            
            return True
        except Exception as e:
            st.warning(f"清空知识库失败: {str(e)}")
            return True
    
    def process_uploaded_file(self, uploaded_file):
        """处理上传的文件，进行OCR识别"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
            # 处理图片文件
            image = uploaded_file.getvalue()
            pil_image = Image.open(BytesIO(image))
            ocr_result = self.ocr_service.detect_from_image(pil_image)
            return " ".join(ocr_result) if ocr_result else ""
            
        elif file_extension == 'pdf':
            # 处理PDF文件
            pdf_bytes = uploaded_file.getvalue()
            pdf_text_dict = self.ocr_service.detect_from_pdf_path(pdf_bytes)
            
            # 合并所有页面的文本
            all_text = []
            for page_num, (img, text_list) in pdf_text_dict.items():
                all_text.extend(text_list)
            
            return " ".join(all_text) if all_text else ""
        
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    def chunk_text(self, text, chunk_size=500, overlap=50):
        """将文本分块"""
        return self.vector_db_service.chunk_text(text, chunk_size, overlap)
    
    def store_in_knowledge_base(self, text_chunks, document_id):
        """将文本块存储到知识库"""
        return self.vector_db_service.store_document_chunks(document_id, text_chunks)
    
    def search_knowledge_base(self, query, top_k=5):
        """在知识库中搜索相似文本块"""
        return self.vector_db_service.search_similar_chunks(query, top_k)


def main():
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 页面配置
    st.set_page_config(page_title="智能问答(Simple_KB)", layout="wide", menu_items={})
    st.subheader(f"🤖 智能问答(Simple_KB)")
    
    # 初始化应用
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = SmartQAKB()
    
    qa_system = st.session_state.qa_system
    
    # 初始化知识库
    if not qa_system.initialize_knowledge_base():
        st.error("知识库初始化失败，无法继续操作")
        return
    
    # 检查知识库是否有内容
    has_content = False
    try:
        search_results = qa_system.search_knowledge_base("test", top_k=1)
        has_content = len(search_results) > 0
    except:
        has_content = False
    
    # 文件上传区域
    with st.expander("上传文档文件", expanded=not has_content):
        uploaded_file = st.file_uploader("选择文件", type=["jpg", "jpeg", "png", "bmp", "pdf"])
        
        if uploaded_file:
            st.success(f"已上传: {uploaded_file.name}")
    
    # 创建三列布局
    col1, col2, col3 = st.columns(3, gap="medium")
    
    # 左侧列：问答区域
    with col1:
        st.divider()
        
        # 如果有内容但没有上传文件，显示直接提问区域
        if has_content and uploaded_file is None:
            st.success("💡 知识库已有内容，您可以直接提问")
        
        # 显示问答区域
        user_input = st.text_area(
            label="请输入您的问题",            
            height=100
        )
        
        # 处理按钮
        if uploaded_file:
            if st.button("重建知识库", type="primary"):
                with st.spinner("正在重建知识库..."):
                    try:
                        # 清空现有知识库
                        qa_system.clear_knowledge_base()
                        
                        # 重新初始化服务
                        st.session_state.qa_system.vector_db_service = VectorDBService()
                        qa_system = st.session_state.qa_system
                        
                        # OCR识别
                        ocr_text = qa_system.process_uploaded_file(uploaded_file)
                        
                        if not ocr_text.strip():
                            st.error("OCR识别失败或未识别到文本内容")
                            return
                        
                        st.success(f"OCR识别完成，识别到 {len(ocr_text)} 个字符")
                        
                        # 文本分块
                        text_chunks = qa_system.chunk_text(ocr_text)
                        st.success(f"文本分块完成，共 {len(text_chunks)} 个块")
                        
                        # 存储到知识库
                        document_id = f"doc_{int(time())}"
                        stored_count = qa_system.store_in_knowledge_base(text_chunks, document_id)
                        st.success(f"知识库构建完成，存储了 {stored_count} 个文本块")
                        
                        # 保存处理状态
                        st.session_state.knowledge_base = {
                            'document_id': document_id,
                            'ocr_text': ocr_text,
                            'chunk_count': len(text_chunks),
                            'kb_name': qa_system.kb_name
                        }
                        
                        st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"处理文件时出错: {str(e)}")
        
        # 智能问答按钮
        if st.button("智能问答", type="secondary"):
            if not user_input.strip():
                st.error("请输入问题内容")
                return
            
            with st.spinner("正在查询知识库..."):
                try:
                    search_results = qa_system.search_knowledge_base(user_input, top_k=3)
                    st.session_state.search_results = search_results
                    st.session_state.user_query = user_input
                    st.success(f"找到 {len(search_results)} 个相关文本块")
                    
                except Exception as e:
                    st.error(f"查询时出错: {str(e)}")
    
    # 中间列：搜索结果
    with col2:
        st.divider()
        
        # 显示OCR原始文本（如果有新上传的文档）
        if 'knowledge_base' in st.session_state:
            st.info("文档内容预览")
            ocr_text_preview = st.session_state.knowledge_base['ocr_text'][:500] + "..." if len(st.session_state.knowledge_base['ocr_text']) > 500 else st.session_state.knowledge_base['ocr_text']
            st.text_area(
                label="原始文本预览",
                value=ocr_text_preview,
                height=200,
                disabled=True
            )
        
        # 显示搜索结果
        if 'search_results' in st.session_state:
            st.info("检索到的相关信息")
            for i, result in enumerate(st.session_state.search_results):
                with st.expander(f"相关文本块 {i+1} (相似度: {result['score']:.3f})"):
                    st.text(result['text'])
    
    # 右侧列：大模型回答
    with col3:
        st.divider()
        
        # 显示大模型回答
        if 'search_results' in st.session_state:
            st.info("智能分析结果")
            
            # 构建提示词
            query = st.session_state.user_query
            context_parts = [result['text'] for result in st.session_state.search_results]
            context = "\n\n".join(context_parts)
            
            system_prompt = """你是一个专业的文档分析助手。请基于提供的文档内容，准确回答用户的问题。
            要求：
            1. 只基于提供的文档内容回答，不要编造信息
            2. 如果文档中没有相关信息，请明确说明"未找到相关信息"
            3. 回答要准确、简洁、专业"""
            
            prompt = f"""基于以下文档内容，请回答用户的问题。

文档内容：
{context}

用户问题：{query}

请根据文档内容，准确提取相关信息并给出回答。"""
            
            # 集成大模型API
            try:
                with st.spinner("正在生成智能分析..."):
                    llm_response = text_inference_with_llm(
                        prompt=prompt,
                        system_message=system_prompt,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    if llm_response:
                        st.text_area(
                            label="分析结果",
                            value=llm_response,
                            height=200,
                            disabled=False
                        )
                    else:
                        st.warning("大模型服务暂时不可用，请稍后重试")
                        
            except Exception as e:
                st.error(f"大模型调用失败: {str(e)}")
                st.text_area(
                    label="分析结果",
                    value="大模型服务调用失败，请检查服务配置。",
                    height=200,
                    disabled=True
                )
            
            # 显示处理统计
            if 'knowledge_base' in st.session_state:
                st.info("知识库统计")
                st.write(f"- 知识库名称: {st.session_state.knowledge_base['kb_name']}")
                st.write(f"- 文档ID: {st.session_state.knowledge_base['document_id']}")
                st.write(f"- 文本字符数: {len(st.session_state.knowledge_base['ocr_text'])}")
                st.write(f"- 文本块数量: {st.session_state.knowledge_base['chunk_count']}")


if __name__ == '__main__':
    main()
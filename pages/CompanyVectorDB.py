import streamlit as st
import tempfile
import os
from pathlib import Path
from service.VectorDBService import VectorDBService


def main():
    st.set_page_config(page_title="公司名向量库", layout="wide", menu_items={})
    st.subheader("🏢 公司名向量库")
    
    # 初始化向量数据库服务
    try:
        vector_db = VectorDBService()
    except Exception as e:
        st.error(f"初始化向量数据库服务失败: {e}")
        st.stop()
    
    # 获取集合信息
    try:
        collection_info = vector_db.get_collection_info()
        st.info(f"当前向量库状态: 包含 {collection_info['points_count']} 个公司名称")
    except Exception as e:
        st.warning(f"获取向量库信息失败: {e}")
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📤 上传公司名文件")
        
        # 文件上传组件
        uploaded_file = st.file_uploader(
            "选择TXT文件", 
            type=['txt'],
            help="请上传包含公司名称的TXT文件，每行一个公司名"
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            file_details = {
                "文件名": uploaded_file.name,
                "文件大小": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.write("文件信息:", file_details)
    
    with col2:
        st.subheader("🔍 搜索功能")
        
        # 搜索说明
        st.info("""🔤 基于语义的文本搜索

搜索原理：
1. 使用BAAI/bge-small-zh-v1.5模型
2. 提取文本语义特征向量
3. 基于语义相似度匹配""")
        
        # 搜索框
        search_query = st.text_input("搜索公司名", placeholder="输入公司名进行搜索...")
        
        if search_query:
            with st.spinner("正在搜索..."):
                try:
                    results = vector_db.search_companies(search_query, limit=5)
                    
                    if results:
                        st.success(f"找到 {len(results)} 个相关结果:")
                        for i, result in enumerate(results, 1):
                            st.write(f"{i}. {result['company_name']} (语义相似度: {result['score']:.3f})")
                    else:
                        st.info("未找到相关公司名")
                except Exception as e:
                    st.error(f"搜索失败: {e}")    
   
    
    if uploaded_file is not None:
        # 解析文件内容
        try:
            file_content = uploaded_file.getvalue().decode('utf-8')
            companies = [line.strip() for line in file_content.split('\n') if line.strip()]
            
            # 更新按钮
            if st.button("🚀 更新向量库", type="primary"):
                with st.spinner("正在更新向量库，这可能需要一些时间..."):
                    try:
                        added_count = vector_db.add_companies(companies)
                        
                        if added_count > 0:
                            st.success(f"✅ 成功添加 {added_count} 个公司名到向量库！")
                            
                            # 验证数据是否真的添加成功
                            if companies:
                                test_company = companies[0]  # 用第一个公司名验证
                                st.info(f"正在验证数据添加情况...")
                                if vector_db.verify_data_added(test_company):
                                    st.success("✅ 数据验证成功，公司名已正确添加到向量库")
                                else:
                                    st.warning("⚠️ 数据验证失败，请检查向量库连接")
                            
                            # 更新集合信息显示
                            collection_info = vector_db.get_collection_info()
                            st.info(f"当前向量库状态: 包含 {collection_info['points_count']} 个公司名称")
                        else:
                            st.warning("⚠️ 没有有效的公司名可以添加")
                            
                    except Exception as e:
                        st.error(f"❌ 更新向量库失败: {e}")
        
        except Exception as e:
            st.error(f"解析文件失败: {e}")


if __name__ == "__main__":
    main()
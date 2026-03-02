import streamlit as st
from dotenv import load_dotenv

from service.CompanyMatchService import CompanyMatchService


def main():
    load_dotenv()
    st.set_page_config(page_title="公司名匹配测试", layout="wide", menu_items={})
    st.subheader("🏢 公司名匹配测试")
    
    # 初始化服务
    try:
        match_service = CompanyMatchService()
    except Exception as e:
        st.error(f"初始化服务失败: {e}")
        st.stop()
    
    # 创建左右两列布局
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("📝 输入查询")
        
        # 输入要查询的公司名
        search_query = st.text_input(
            "输入要查询的公司名", 
            placeholder="请输入要匹配的公司名称...",
            key="search_input"
        )
        
        # 上传公司名单
        st.subheader("📤 上传名单")
        uploaded_file = st.file_uploader(
            "选择TXT文件", 
            type=['txt'],
            help="每行一个公司名，支持批量导入"
        )
        
        # 匹配按钮
        if st.button("🚀 开始匹配", type="primary", use_container_width=True):
            if not search_query:
                st.warning("⚠️ 请输入要查询的公司名")
            elif not uploaded_file:
                st.warning("⚠️ 请上传公司名单文件")
            else:
                # 解析文件内容
                try:
                    file_content = uploaded_file.getvalue().decode('utf-8')
                    companies = [line.strip() for line in file_content.split('\n') if line.strip()]
                    
                    if companies:
                        # 清空现有数据并导入新数据
                        match_service.companies.clear()
                        match_service.add_companies(companies)
                        
                        st.success(f"✅ 成功导入 {len(companies)} 个公司名")
                        
                        # 立即进行匹配
                        with st.spinner("正在匹配..."):
                            try:
                                results = match_service.search_companies(search_query, limit=10)
                                
                                # 将结果存入session state以便右侧显示
                                st.session_state.match_results = results
                                st.session_state.search_query = search_query
                                
                            except Exception as e:
                                st.error(f"匹配失败: {e}")
                    else:
                        st.warning("⚠️ 文件中没有有效的公司名")
                
                except Exception as e:
                    st.error(f"解析文件失败: {e}")
    
    with right_col:
        st.subheader("📊 匹配结果")
        
        # 显示匹配结果
        if 'match_results' in st.session_state and st.session_state.match_results:
            results = st.session_state.match_results
            search_query = st.session_state.search_query
            
            st.success(f"🔍 查询: **{search_query}**")
            st.success(f"✅ 找到 {len(results)} 个匹配结果:")
            
            for i, result in enumerate(results, 1):
                with st.container():
                    st.write(f"**{i}. {result['company_name']}**")
                    st.write(f"   相似度: {result['score']:.3f} | 编辑距离: {result['distance']}")
                    st.divider()
        
        elif 'match_results' in st.session_state and not st.session_state.match_results:
            st.info("❌ 未找到匹配的公司名")
        
        else:
            st.info("💡 请在左侧输入查询内容并上传名单文件，然后点击'开始匹配'按钮")


if __name__ == "__main__":
    main()
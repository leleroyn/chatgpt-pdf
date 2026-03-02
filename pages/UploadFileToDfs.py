import os

import requests
import streamlit as st
from dotenv import load_dotenv


def main():
    load_dotenv()
    st.set_page_config(page_title="上传文件到DFS服务器", layout="wide", menu_items={})
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
           font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("📤 上传文件到DFS服务器")
    
    uploaded_file = st.file_uploader("上传文件", type=["png", "jpg", "bmp", "pdf", "zip"])
    
    if uploaded_file is not None:
        with st.spinner("正在上传文件..."):
            url = os.getenv("DFS_URL")
            files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
            r = requests.post(url, files=files)
            st.success(f"✅ 文件上传成功: {uploaded_file.name}")
            st.json(r.text)
    else:
        st.info("💡 请上传文件到DFS服务器")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传文件**: 点击上方上传按钮，选择文件
            2. **支持格式**: PNG, JPG, BMP, PDF, ZIP
            3. **操作流程**: 上传文件 → 自动上传到DFS服务器 → 查看返回结果
            4. **返回结果**: 显示文件在DFS服务器上的URL
            """)


if __name__ == '__main__':
    main()

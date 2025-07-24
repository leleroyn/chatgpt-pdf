import os

import requests
import streamlit as st


def main():
    st.set_page_config(page_title="上传文件到DFS服务器", layout="wide", menu_items={})
    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
           font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("📤上传文件到DFS服务器")
    uploaded_file = st.file_uploader("上传文件", type=["png", "jpg", "bmp", "pdf", "zip"])
    if uploaded_file is not None:
        url = os.getenv("DFS_URL")
        files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
        r = requests.post(url, files=files)
        st.info("上传成功.")
        st.json(r.text)


if __name__ == '__main__':
    main()

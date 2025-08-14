import io
from base64 import b64decode
from time import time

import streamlit as st

from service import *
from service.IPService import IPService


def main():
    st.set_page_config(page_title="印章提取(Paddle)", layout="wide", menu_items={})
    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
        font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("📕印章提取(Paddle)")
    uploaded_file = st.file_uploader("上传文件", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            st.image(image)
        with columns[1]:
            start = time()
            ips_service = IPService()
            byte_stream = io.BytesIO()
            image.save(byte_stream, format='PNG')
            byte_data = byte_stream.getvalue()
            results = ips_service.seal_preprocess(byte_data, tool=(0.6, True, True))
            if not results:
                st.info("没有检测到任何印章.")
                return
            end = time()
            elapsed1 = end - start
            for res in results:
                st.write(res["ocr_result"])
                st.divider()
            st.info(f"提取花费：***{elapsed1}***s")


if __name__ == '__main__':
    main()

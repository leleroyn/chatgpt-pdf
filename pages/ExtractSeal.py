import io
from base64 import b64decode
from time import time

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from service.IPService import IPService


def main():
    load_dotenv()
    st.set_page_config(page_title="检测图片中的印章", layout="wide", menu_items={})
    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
        font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("📕检测图片中的印章")
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
            results = ips_service.seal_preprocess(byte_data, return_seal_image=True,return_ocr_text=False, tool=(0.6, False, False))
            if not results:
                st.info("没有检测到任何印章.")
                return
            end = time()
            elapsed = end - start
            st.info(f"提取完成，花费：{elapsed}")
            item = 1
            for res in results:
                image_bytes = b64decode(res["seal_image_base64"])
                image_stream = io.BytesIO(image_bytes)  # 字节流转为内存文件对象
                image = Image.open(image_stream)
                st.image(image)
                st.info(f"目标 {item}: ***{ips_service.convert_seal_type(res['seal_type'])}*** | "
                        f"置信度: {res['confidence']} "
                        )
                item = item + 1


if __name__ == '__main__':
    main()

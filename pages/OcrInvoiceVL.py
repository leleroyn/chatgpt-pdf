import io
from time import time

import streamlit as st

from service import *
from service.OcrService import resize_image


def main():
    llm = "qwen2.5vl:7b"
    st.set_page_config(page_title="发票信息提取", layout="wide", menu_items={})
    st.subheader(f"🐻发票信息提取({llm})")
    uploaded_file = st.file_uploader("上传发票信息影像", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            image = resize_image(image, 1000)
            st.image(image)
        with columns[1]:
            with st.spinner("Please waiting..."):
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                start = time()
                oneApiService = OneApiService(llm)
                try:
                    res = oneApiService.ocr_invoice_vl(byte_data)
                except Exception as r:
                    st.warning('未知错误 %s' % r)
                else:
                    end = time()
                    elapsed2 = end - start
                    st.info("提取完成花费:{}s".format(elapsed2))
                    st.write(res)


if __name__ == '__main__':
    main()

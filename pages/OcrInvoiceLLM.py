import io
from time import time

import streamlit as st

from service import *


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title=" 发票信息提取", layout="wide", menu_items={})
    st.subheader(f"🐋发票信息提取(OCR+{llm})")
    uploaded_file = st.file_uploader("上传发票影像", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            st.image(image)
        with columns[1]:
            with st.spinner("Please waiting..."):
                start = time()
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                paddleOcr = PaddleOcrService()
                text = paddleOcr.ocr_text(byte_data)
                end = time()
                elapsed1 = end - start
                st.info("OCR完成花费:{}s".format(elapsed1))
                st.write(text)
                start = time()
                oneApiService = OneApiService(llm)
                res = oneApiService.ocr_invoice_llm(text)
                end = time()
                elapsed2 = end - start
                st.info("提取完成花费:{}s".format(elapsed2))
                st.write(res)


if __name__ == '__main__':
    main()

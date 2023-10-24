from time import time
import streamlit as st
from service import *


def main():
    st.set_page_config(page_title="PDF文字提取", layout="wide", menu_items={})
    st.subheader("🔍PDF文字提取")
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Please waiting..."):
            start = time()
            ocr = OcrService()
            res = ocr.detect_from_pdf_path(uploaded_file.getvalue())
            end = time()
            elapsed = end - start
            st.info("识别完成，共花费 {} 秒".format(elapsed))
            for key, value in res.items():
                st.info("第 {} 页".format(key + 1))
                columns = st.columns(2)
                with columns[0]:
                    st.image(value[0])
                with columns[1]:
                    st.info("识别结果：")
                    for txt in value[1]:
                        st.caption(txt)


if __name__ == '__main__':
    main()

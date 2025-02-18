from time import time

import streamlit as st
from PIL import Image

from service import *


def main():
    st.set_page_config(page_title="身份证信息提取", layout="wide", menu_items={})
    st.subheader("🐋身份证信息提取 - DeepSeek")
    uploaded_file = st.file_uploader("上传身份证影像", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            image = orientation(pil2cv(image))
            st.image(toRGB(image))
        with columns[1]:
            with st.spinner("Please waiting..."):
                start = time()
                ocr = OcrService()
                textLines = ocr.detect_from_image_path(uploaded_file)
                end = time()
                elapsed1 = end - start

                start = time()
                oneApiService = OneApiService("DeepSeek-V3")
                text = ""
                for v in textLines:
                    text = text + v + "\n"
                res = oneApiService.ocr_idcard_deepseek(text)

                end = time()
                elapsed2 = end - start
                st.info("提取完成，OCR花费:{}s,AI提取花费:{} s".format(elapsed1, elapsed2))
                st.write(res)


if __name__ == '__main__':
    main()

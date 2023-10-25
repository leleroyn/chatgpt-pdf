from time import time

import streamlit as st
from PIL import Image

from service import *


def main():
    st.set_page_config(page_title="图片文字提取", layout="wide", menu_items={})
    st.subheader("🔍图片文字提取")
    uploaded_file = st.file_uploader("上传图片影像", type=["png", "jpg", "bmp"])
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
                res = ocr.detect_from_image_path(uploaded_file)
                end = time()
                elapsed = end - start
                st.info("识别完成，共花费 {} seconds".format(elapsed))
                for v in res:
                    st.write(v)


if __name__ == '__main__':
    main()

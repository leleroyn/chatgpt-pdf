import io
from time import time

import streamlit as st

from service import *


def main():
    st.set_page_config(page_title="图片文字提取", layout="wide", menu_items={})
    st.subheader("🔍图片文字提取")
    uploaded_file = st.file_uploader("上传图片影像", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            # Convert CMYK to RGB before saving as PNG
            if image.mode == 'CMYK':
                image = image.convert('RGB')
            # Convert to grayscale for display
            image_display = image.convert("L")
            st.image(image_display)
        with columns[1]:
            with st.spinner("Please waiting..."):
                start = time()
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                paddleOcr = PaddleOcrService()
                text = paddleOcr.ocr_text(byte_data)
                end = time()
                elapsed = end - start
                st.info("识别完成，共花费 {} seconds".format(elapsed))
                st.write(text)


if __name__ == '__main__':
    main()

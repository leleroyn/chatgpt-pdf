import io
from time import time

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service import PaddleOcrService


def main():
    load_dotenv()
    st.set_page_config(page_title="图片文字提取", layout="wide", menu_items={})
    st.subheader("🖼️ 图片文字提取")
    
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        uploaded_file = st.file_uploader("上传图片影像", type=["png", "jpg", "bmp"])
    
    if uploaded_file is not None:
        columns = st.columns(2)
        with columns[0]:
            image = Image.open(uploaded_file)
            if image.mode == 'CMYK':
                image = image.convert('RGB')
            image_display = image.convert("L")
            st.image(image_display, caption="原始图像")
        
        with columns[1]:
            with st.spinner("正在提取文字..."):
                start = time()
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                paddleOcr = PaddleOcrService()
                text = paddleOcr.ocr_text(byte_data)
                end = time()
                elapsed = end - start
                st.success(f"✅ 提取完成，耗时: {elapsed:.2f}s")
                st.write(text)
    else:
        st.info("💡 请上传图片后查看文字识别结果")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传图片**: 点击上方上传按钮，选择图片文件
            2. **支持格式**: PNG, JPG, BMP
            3. **操作流程**: 上传图片 → 自动识别文字 → 查看结果
            """)


if __name__ == '__main__':
    main()

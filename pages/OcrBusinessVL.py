import io
import os
from time import time

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service import OneApiService


def main():
    load_dotenv()
    llm = os.getenv("VLM_VERSION")
    st.set_page_config(page_title="企业营业执照信息提取", layout="wide", menu_items={})
    st.subheader(f"🏢 企业营业执照信息提取({llm})")
    
    uploaded_file = st.file_uploader("上传企业营业执照影像", type=["png", "jpg", "bmp"])
    
    if uploaded_file is not None:
        columns = st.columns(2)
        with columns[0]:
            image = Image.open(uploaded_file)
            image = image.convert("L")
            st.image(image, caption="原始图像")
        
        with columns[1]:
            with st.spinner("正在提取营业执照信息..."):
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                start = time()
                oneApiService = OneApiService(llm)
                try:
                    res = oneApiService.ocr_business_vl(byte_data)
                except Exception as r:
                    st.error(f"❌ 提取失败: {str(r)}")
                else:
                    end = time()
                    elapsed2 = end - start
                    st.success(f"✅ 提取完成，耗时: {elapsed2:.2f}s")
                    st.write(res)
    else:
        st.info("💡 请上传营业执照图片后查看提取结果")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传营业执照**: 点击上方上传按钮，选择营业执照图片
            2. **支持格式**: PNG, JPG, BMP
            3. **操作流程**: 上传营业执照 → 使用VL模型提取信息 → 查看结果
            4. **模型说明**: 使用视觉语言模型(VL)进行端到端信息提取
            """)


if __name__ == '__main__':
    main()

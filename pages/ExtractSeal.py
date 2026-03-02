import io
from base64 import b64decode
from time import time
import os

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service.IPService import IPService


def main():
    load_dotenv()
    st.set_page_config(page_title="检测图片中的印章", layout="wide", menu_items={})
    
    st.subheader("🔴 检测图片中的印章")
    
    # Create a more organized layout
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        uploaded_file = st.file_uploader("上传文件", type=["png", "jpg", "bmp", "jpeg"])
    with head_col2:
        conf_size = st.slider('置信度阈值', min_value=0.1, max_value=1.0, step=0.1, value=0.6)
        st.caption("置信度低于阈值的结果将被过滤")
    
    if uploaded_file is not None:
        try:
            # Load and display the image
            image = Image.open(uploaded_file)
            
            # Create a three-tier layout as per UI preference
            # Tier 1: Original image and core detection results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("原始图像")
                with st.expander("查看原始图像"):
                    st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("检测结果")
                with st.spinner("正在检测印章..."):
                    start = time()
                    ips_service = IPService()
                    byte_stream = io.BytesIO()
                    # Convert CMYK to RGB before saving as PNG
                    if image.mode == 'CMYK':
                        image = image.convert('RGB')
                    image.save(byte_stream, format='PNG')
                    byte_data = byte_stream.getvalue()
                    results = ips_service.seal_preprocess(byte_data, return_seal_image=True, return_ocr_text=False, 
                                                        tool=(conf_size, False, False))
                    
                    if not results:
                        st.info("没有检测到任何印章。请尝试调整置信度阈值或上传更清晰的图像。")
                        return
                    
                    end = time()
                    elapsed = end - start
                    
                    # Display detection information
                    item = 1
                    for i, res in enumerate(results):
                        confidence = res['confidence']
                        seal_type = ips_service.convert_seal_type(res['seal_type'])
                        
                        # Only show results above confidence threshold
                        if confidence >= conf_size:
                            st.success(f"检测到印章 #{item}")
                            st.markdown(f"**类型**: {seal_type}")
                            st.markdown(f"**置信值**: {confidence:.2f}")
                            
                            # Display seal image
                            try:
                                image_bytes = b64decode(res["seal_image_base64"])
                                image_stream = io.BytesIO(image_bytes)
                                seal_image = Image.open(image_stream)
                                st.image(seal_image, caption=f"印章图像 #{item}")
                            except Exception as e:
                                st.warning(f"无法显示印章图像: {str(e)}")
                            
                            st.divider()
                            item += 1
                        else:
                            st.warning(f"检测到印章 #{i+1} (置信值: {confidence:.2f}) - 低于阈值被过滤")
                    
                    if item == 1:
                        st.info("所有检测结果的置信度均低于阈值。请尝试降低置信度阈值。")
            
            # Performance metrics
            st.markdown("---")
            st.metric("检测耗时", f"{elapsed:.2f}s")
                
        except Exception as e:
            st.error(f"处理过程中出现错误: {str(e)}")
            st.info("请确保上传的是有效的图像，并检查API服务是否正常运行。")
    else:
        st.info("💡 请上传图片后检测印章")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传图片**: 点击上方上传按钮，选择图片文件
            2. **支持格式**: PNG, JPG, BMP, JPEG
            3. **置信度阈值**: 调整滑块过滤低置信度结果
            4. **操作流程**: 上传图片 → 自动检测印章 → 查看结果
            """)


if __name__ == '__main__':
    main()
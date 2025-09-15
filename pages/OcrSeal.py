import io
import re
from time import time
import json
import os

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service.IPService import IPService
from service.PaddleOcrService import PaddleOcrService


def main():
    load_dotenv()
    st.set_page_config(page_title="印章提取(Paddle)", layout="wide", menu_items={})
    
    st.subheader("🔴印章提取(Paddle)")
    
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
                # Hide original image by default, show in expander
                with st.expander("查看原始图像"):
                    st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("检测结果")
                with st.spinner("正在提取印章信息..."):
                    start = time()
                    ips_service = IPService()
                    byte_stream = io.BytesIO()
                    image.save(byte_stream, format='PNG')
                    byte_data = byte_stream.getvalue()
                    results = ips_service.seal_preprocess(byte_data, return_seal_image=True, return_ocr_text=True,
                                                        tool=(conf_size, True, True))
                    
                    if not results:
                        st.info("没有检测到任何印章。请尝试调整置信度阈值或上传更清晰的图像。")
                        return
                    
                    end = time()
                    elapsed1 = end - start
                    
                    # Display detection information
                    for i, res in enumerate(results):
                        confidence = res['confidence']
                        seal_type = ips_service.convert_seal_type(res['seal_type'])
                        
                        # Only show results above confidence threshold
                        if confidence >= conf_size:
                            st.success(f"检测到印章 #{i+1}")
                            st.markdown(f"**类型**: {seal_type}")
                            st.markdown(f"**置信值**: {confidence:.2f}")
                            
                            # Display OCR result
                            if "ocr_result" in res:
                                # Clean the OCR result
                                result = re.sub(r'[a-zA-Z\d\s|_]', '', res["ocr_result"], flags=re.IGNORECASE | re.UNICODE)
                                st.markdown("**OCR识别结果**:")
                                st.write(f'***{result}***') 
                            st.divider()
                        else:
                            st.warning(f"检测到印章 #{i+1} (置信值: {confidence:.2f}) - 低于阈值被过滤")
            

                st.metric("提取耗时", f"{elapsed1:.2f}s")
                
        except Exception as e:
            st.error(f"处理过程中出现错误: {str(e)}")
            st.info("请确保上传的是有效的图像，并检查API服务是否正常运行。")


if __name__ == '__main__':
    main()
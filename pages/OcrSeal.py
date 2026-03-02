from base64 import b64decode
import io
import re
from time import time
import json
import os
import requests

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service.IPService import IPService
from service.PaddleOcrService import PaddleOcrService


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title="印章提取", layout="wide", menu_items={})
    
    st.subheader("🔴 印章提取")
    
    head_col1, head_col2, head_col3 = st.columns([2, 1, 1])
    
    with head_col1:
        uploaded_file = st.file_uploader(
            "上传印章图片", 
            type=["png", "jpg", "bmp", "jpeg", "pdf"],
            help="支持 PNG, JPG, BMP, JPEG, PDF 格式文件"
        )
    with head_col2:
        conf_size = st.slider(
            '置信度阈值', 
            min_value=0.1, 
                max_value=1.0, 
                step=0.1, 
                value=0.6,
                help="置信度低于此阈值的结果将被过滤"
            )
        with head_col3:
            third_party_options = st.selectbox(
                "第三方识别引擎",
                ["禁用","启用"],
                help="启用后将使用第三方引擎进行印章内容识别"
            )   
    
    if uploaded_file is not None:
        try:
            # Load the image or PDF
            if uploaded_file.type != "application/pdf":
                # Load the image for display only
                image = Image.open(uploaded_file)
            
            # Create a three-tier layout as per UI preference
            # Tier 1: Original file and core detection results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("原始文件")
                # Hide original file by default, show in expander
                with st.expander("查看原始文件"):
                    if uploaded_file.type == "application/pdf":
                        st.write(f"PDF 文件: {uploaded_file.name}")
                        st.info("PDF 文件内容预览暂不支持")
                    else:
                        st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("🔍 检测结果")
                with st.spinner("正在提取印章信息..."):
                    start = time()
                    ips_service = IPService()
                    byte_data = uploaded_file.getvalue()
                    
                    file_type = "pdf" if uploaded_file.type == "application/pdf" else "image"
                    results = ips_service.seal_preprocess(byte_data, file_type=file_type, return_seal_image=True, return_ocr_text=True,
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
                            with st.expander(f"检测到印章 #{i+1} - {seal_type} (置信值: {confidence:.2f})", expanded=True):
                                image_bytes = b64decode(res["seal_image_base64"])
                                image_stream = io.BytesIO(image_bytes)
                                seal_image = Image.open(image_stream)
                                st.image(seal_image)
                                # Display OCR result if available
                                if "ocr_result" in res:
                                    # Clean the OCR result
                                    result = re.sub(r'[a-zA-Z\d\s|_]', '', res["ocr_result"], flags=re.IGNORECASE | re.UNICODE)
                                    st.markdown("**🤖 本地OCR识别结果**:")
                                    st.info(f"{result}")                               
                                
                                # Show third-party OCR engine results if enabled
                                if third_party_options == "启用" and "seal_image_base64" in res:
                                    with st.spinner("正在调用第三方识别引擎..."):
                                        try:                                          
                                            import requests
                                            third_party_url = os.getenv('THIRD_PARTY_OCR_SEAL_URL')
                                            if not third_party_url:
                                                st.warning("未配置 THIRD_PARTY_OCR_SEAL_URL 环境变量")
                                            else:                                              
                                                base64_content = res["seal_image_base64"]                                              
                                                response = requests.post(
                                                    third_party_url,
                                                    data=base64_content,
                                                    headers={'Content-Type': 'text/plain'}
                                                )                                                
                                                if response.status_code == 200:
                                                    response_data = response.json()
                                                    
                                                    if response_data.get("isSuccess"):
                                                        st.markdown("**🌐 第三方识别结果**:")
                                                        stamp_data = response_data.get("data", {}).get("stamp", [])
                                                        
                                                        for idx, stamp in enumerate(stamp_data):
                                                            st.info(f"{stamp.get('value', 'N/A')}")
                                                            
                                                    else:
                                                        st.warning(f"第三方识别失败: {response_data.get('message', 'Unknown error')}")
                                                else:
                                                    st.warning(f"第三方API请求失败，状态码: {response.status_code}")
                                        except Exception as ex:
                                            st.warning(f"调用第三方识别引擎时出现错误: {str(ex)}")
                        else:
                            st.warning(f"检测到印章 #{i+1} (置信值: {confidence:.2f}) - 低于阈值被过滤")
                    
                    st.markdown(f"**⏱️ 总提取耗时: {elapsed1:.2f}秒**")
            

                
        except Exception as e:
            st.error(f"❌ 处理过程中出现错误: {str(e)}")
            st.info("💡 请确保上传的是有效的图像，并检查API服务是否正常运行。")
    else:
        st.info("💡 请上传图片后提取印章信息")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传图片**: 点击上方上传按钮，选择图片文件
            2. **支持格式**: PNG, JPG, BMP, JPEG, PDF
            3. **置信度阈值**: 调整滑块过滤低置信度结果
            4. **第三方识别**: 可启用第三方引擎进行更精确的识别
            5. **操作流程**: 上传图片 → 提取印章 → 查看OCR结果
            """)


    st.markdown("---")
    st.markdown("### 📌 提示")
    st.info("1. 上传清晰的印章图片以获得更好的识别效果\n2. 调整置信度阈值以控制识别结果的准确性\n3. 启用第三方识别引擎可获得更精确的识别结果")

if __name__ == '__main__':
    main()
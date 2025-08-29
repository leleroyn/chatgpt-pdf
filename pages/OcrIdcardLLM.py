import io
from time import time
import json
import os

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from service.IPService import IPService
from service.OneApiService import OneApiService


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title="身份证信息提取", layout="wide", menu_items={})
    st.subheader(f"👤 身份证信息提取(OCR+{llm})")
    
    # Create a more organized layout
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        uploaded_file = st.file_uploader("上传身份证影像", type=["png", "jpg", "bmp", "jpeg"])
    with head_col2:
        conf_size = st.slider('置信度阈值', min_value=0.1, max_value=1.0, step=0.1, value=0.8)
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
                with st.expander("显示原始图像"):
                    st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("检测结果")
                with st.spinner("正在检测身份证信息..."):
                    ips_service = IPService()
                    byte_stream = io.BytesIO()
                    image.save(byte_stream, format='PNG')
                    byte_data = byte_stream.getvalue()
                    
                    start = time()
                    results = ips_service.idcard_preprocess(byte_data, return_ocr_text=True, return_corp_image=True,
                                                            tool=(conf_size, True, False))
                    
                    if not results:
                        st.info("没有检测到任何身份证。请尝试调整置信度阈值或上传更清晰的图像。")
                        return
                    
                    # Check for valid ID card (front side)
                    has_valid_idcard = False
                    for res in results:
                        if res.get('idcard_type') == 1:
                            has_valid_idcard = True
                            break
                    
                    if not has_valid_idcard:
                        st.warning("证件不完整：未检测到有效的身份证类型（正面）")
                        return
                    
                    end = time()
                    elapsed1 = end - start
                    
                    # Display detection information
                    ocr_result = []
                    
                    for i, res in enumerate(results):
                        confidence = res['confidence']
                        idcard_type = ips_service.convert_idcard_type(res['idcard_type'])
                        
                        # Only show results above confidence threshold
                        if confidence >= conf_size:
                            st.success(f"检测到身份证 #{i+1}")
                            st.markdown(f"**类型**: {idcard_type}")
                            st.markdown(f"**置信值**: {confidence:.2f}")
                            ocr_result.append(res["ocr_text"])
                            st.divider()
                        else:
                            st.warning(f"检测到身份证 #{i+1} (置信值: {confidence:.2f}) - 低于阈值被过滤")
                    
                    if not ocr_result:
                        st.info("所有检测结果的置信度均低于阈值。请尝试降低置信度阈值。")
                        return
            
            # Tier 2: Separator line
            st.markdown("---")
            
            # Tier 3: Detailed information at the bottom
            st.subheader("详细信息提取")
            
            # Combine OCR results
            ocr_text = "\n".join(ocr_result)
            
            # Process with LLM
            with st.spinner("正在提取身份证信息..."):
                start = time()
                oneApiService = OneApiService(llm)
                res = oneApiService.ocr_idcard_llm(ocr_text)
                end = time()
                elapsed3 = end - start
            
            # Display LLM results (prioritized content)
            st.markdown("#### 🎯 AI提取结果")
            if res:
                try:
                    # Try to parse as JSON
                    parsed_result = json.loads(res)
                    st.json(parsed_result)
                except json.JSONDecodeError:
                    # If not JSON, display as text
                    st.text_area("LLM提取结果", res, height=300, key="llm_result")
            else:
                st.warning("LLM服务未返回结果，请检查服务配置。")
            
            # Display OCR text in an expander to save space
            with st.expander("🔍 查看OCR识别详情"):
                st.text_area("OCR识别结果", ocr_text, height=200, key="ocr_text")
            
            # Display detection details with cropped images (avoiding nested expanders)
            st.markdown("#### 📋 检测详情")
            tabs = st.tabs([f"身份证 #{i+1}" for i in range(len([r for r in results if r['confidence'] >= conf_size]))])
            
            valid_result_index = 0
            for i, res in enumerate(results):
                confidence = res['confidence']
                if confidence >= conf_size:
                    with tabs[valid_result_index]:
                        st.markdown(f"**类型**: {ips_service.convert_idcard_type(res['idcard_type'])}")
                        st.markdown(f"**置信值**: {confidence:.2f}")
                        
                        # Display cropped image
                        try:
                            cropped_image = ips_service.base64_to_pil(res['corp_image_base64'])
                            st.markdown("**裁剪图像**:")
                            st.image(cropped_image, caption=f"裁剪图像 #{i+1}", use_column_width=True)
                        except Exception as e:
                            st.warning(f"无法显示裁剪图像: {str(e)}")
                        
                        # Display OCR text for this result
                        st.markdown("**OCR识别文本**:")
                        st.text_area(f"OCR文本 #{i+1}", res["ocr_text"], height=150, key=f"ocr_detail_{i+1}")
                    
                    valid_result_index += 1
            
            # Performance metrics
            st.markdown("---")
            col3, col4 = st.columns(2)
            with col3:
                st.metric("检测耗时", f"{elapsed1:.2f}s")
            with col4:
                st.metric("信息提取耗时", f"{elapsed3:.2f}s")
                
        except Exception as e:
            st.error(f"处理过程中出现错误: {str(e)}")
            st.info("请确保上传的是有效的身份证图像，并检查API服务是否正常运行。")


if __name__ == '__main__':
    main()
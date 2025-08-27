import io
from time import time

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from service import *
from service.IPService import IPService


def main():
    load_dotenv()
    st.set_page_config(page_title="卡片检测识别", layout="wide", menu_items={})
    st.subheader("🔍卡片检测识别")
    
    # Header section with file uploader and options
    head_col = st.columns(2)
    with head_col[0]:
        uploaded_file = st.file_uploader("上传卡片图像", type=["png", "jpg", "jpeg", "bmp"])
    with head_col[1]:
        return_corp_image = st.checkbox('返回裁剪图像', value=False, help="是否返回检测到的卡片裁剪图像")
    
    # Main content columns
    columns = st.columns(2)
    
    if uploaded_file is not None:
        with columns[0]:
            st.markdown("### 📷 原始图像")
            image = Image.open(uploaded_file)
            st.image(image, caption="上传的图像")
        
        with columns[1]:
            st.markdown("### 📊 检测结果")
            with st.spinner("正在检测卡片类型..."):
                try:
                    # Initialize service
                    ips_service = IPService()
                    
                    # Convert image to bytes
                    byte_stream = io.BytesIO()
                    image.save(byte_stream, format='PNG')
                    byte_data = byte_stream.getvalue()
                    
                    # Call card detection API
                    start = time()
                    result = ips_service.card_det(byte_data, return_corp_image=return_corp_image)
                    end = time()
                    elapsed_time = end - start
                    
                    # Display results
                    if result:
                        # Display card information
                        card_info = result.get('card_info', {})
                        card_type = card_info.get('card_type', 0)
                        confidence = card_info.get('confidence', 0)
                        fork_status = result.get('fork', False)
                        
                        # Check confidence threshold - hide results if below 0.8
                        if confidence < 0.8:
                            st.warning(f"⚠️ 检测置信度过低 ({confidence:.3f} < 0.8)，检测结果不可靠")
                            st.info("💡 建议：请尝试上传更清晰、光线更好的图像")
                            return
                        
                        # Convert card type to Chinese description
                        card_type_desc = ips_service.convert_card_type(card_type)
                        
                        # Display basic detection metrics in a compact layout
                        metrics_col1, metrics_col2 = st.columns(2)
                        with metrics_col1:
                            st.metric("卡片类型", card_type_desc, help=f"检测到的卡片类型代码: {card_type}")
                            # Document authenticity
                            photocopy_status = "复印件" if fork_status else "原件"
                            photocopy_color = "🟡" if fork_status else "🟢"
                            st.metric("文档类型", f"{photocopy_color} {photocopy_status}", 
                                    help="检测文档是原件还是复印件")
                        
                        with metrics_col2:
                            st.metric("置信度", f"{confidence:.3f}", help="检测结果的置信度分数")
                            # Processing status
                            processing_status = "检测成功"
                            status_color = "🟢"
                            st.metric("处理状态", f"{status_color} {processing_status}", 
                                    help="文档检测处理状态")
                        
                        # Display processing time
                        st.success(f"✅ 检测完成，耗时: {elapsed_time:.3f} 秒")
                        
                    else:
                        st.warning("⚠️ 未检测到任何卡片信息")
                        
                except Exception as e:
                    st.error(f"❌ 检测过程中发生错误: {str(e)}")
                    st.exception(e)
        
        # Display cropped image and detailed information in a new row below
        if uploaded_file is not None and 'result' in locals() and result:
            card_info = result.get('card_info', {})
            confidence = card_info.get('confidence', 0)
            
            # Only show additional details if confidence is sufficient
            if confidence >= 0.8:
                st.markdown("---")  # Separator line
                
                # Create two columns for cropped image and detailed info
                detail_col1, detail_col2 = st.columns([1, 1])
                
                with detail_col1:
                    # Display cropped image if available
                    if return_corp_image and result.get('corp_image_base64'):
                        st.markdown("### 🎯 检测区域")
                        try:
                            cropped_image = ips_service.base64_to_pil(result['corp_image_base64'])
                            st.image(cropped_image, caption="检测到的卡片区域", use_column_width=True)
                        except Exception as e:
                            st.error(f"无法显示裁剪图像: {str(e)}")
                    else:
                        st.info("📝 未启用图像裁剪或无裁剪结果")
                
                with detail_col2:
                    # Display detailed results in expandable section
                    st.markdown("### 📋 详细信息")
                    with st.expander("查看详细检测数据", expanded=True):
                        card_info = result.get('card_info', {})
                        card_type = card_info.get('card_type', 0)
                        confidence = card_info.get('confidence', 0)
                        fork_status = result.get('fork', False)
                        card_type_desc = ips_service.convert_card_type(card_type)
                        
                        detection_details = {
                            "card_type_code": card_type,
                            "card_type_description": card_type_desc,
                            "confidence": confidence,
                            "is_photocopy": fork_status,
                            "document_authenticity": "复印件" if fork_status else "原件",
                            "photocopy_detection_confidence": "High" if fork_status else "N/A",
                            "has_cropped_image": bool(result.get('corp_image_base64')),
                            "processing_time_seconds": elapsed_time
                        }
                        st.json(detection_details)
    
    else:
        # Display instructions when no file is uploaded
        with st.container():
            st.markdown("""
            ### 📖 使用说明
            
            1. **上传图像**: 点击上方的文件上传器，选择包含卡片的图像文件
            2. **支持格式**: PNG, JPG, JPEG, BMP
            3. **检测类型**: 系统可以识别以下卡片类型：
               - 🆔 身份证
               - 🏢 营业执照  
               - 🧾 发票
               - 📄 其他类型
            4. **结果展示**: 检测完成后将显示卡片类型、置信度、复印件检测和裁剪图像
            5. **质量要求**: 只有置信度 ≥ 0.8 的检测结果才会显示，低于该阈值将被视为检测失败
            
            ### 🔧 功能特点
            - ✨ 智能卡片检测与分类
            - 🔍 **复印件检测**: 智能判断文档是原件还是复印件
            - 🎯 自动图像裁剪
            - 📊 置信度评估
            - ⚡ 快速处理
            - 🛡️ 文档真实性验证
            - 🎯 **质量保障**: 只显示高置信度(≥0.8)的检测结果
            """)


if __name__ == '__main__':
    main()
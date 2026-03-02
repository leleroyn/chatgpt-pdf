import io
from time import time

import streamlit as st
from dotenv import load_dotenv

from service import OcrService


def main():
    load_dotenv()
    st.set_page_config(page_title="PDF文字提取", layout="wide", menu_items={})
    st.subheader("📄 PDF文字提取")
    
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("正在提取文字..."):
            start = time()
            ocr = OcrService()
            res = ocr.detect_from_pdf_path(uploaded_file.getvalue())
            end = time()
            elapsed = end - start
            st.success(f"✅ 提取完成，耗时: {elapsed:.2f}s")
            
            for key, value in res.items():
                st.info(f"第 {key + 1} 页")
                columns = st.columns(2)
                with columns[0]:
                    st.image(value[0], caption=f"第 {key + 1} 页")
                with columns[1]:
                    st.markdown("**识别结果：**")
                    for txt in value[1]:
                        st.caption(txt)
    else:
        st.info("💡 请上传PDF文件后查看文字识别结果")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传PDF**: 点击上方上传按钮，选择PDF文件
            2. **支持格式**: PDF
            3. **操作流程**: 上传PDF → 自动识别每页文字 → 查看结果
            """)


if __name__ == '__main__':
    main()

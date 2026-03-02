import base64
from time import time

import streamlit as st
from dotenv import load_dotenv

from service import pdf_to_pic, pic_to_pdf


def main():
    load_dotenv()
    st.set_page_config(page_title="PDF压缩", layout="wide", menu_items={})
    st.subheader("🗜️ PDF压缩")

    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    with head_col2:
        compress_size = st.slider('压缩到大小(M)', min_value=1, max_value=20, step=1, value=10)
        st.caption("目标压缩文件大小")

    if uploaded_file is not None:
        with st.spinner("正在压缩PDF..."):
            if len(uploaded_file.getvalue()) < compress_size * 1024 * 1024:
                st.warning(f"⚠️ 上传的文件小于目标大小 {compress_size}M，无需压缩")
                return
            start = time()
            ret_size = len(uploaded_file.getvalue())
            ratio = 40
            pdf_bits = None
            while compress_size * 1024 * 1024 < ret_size:
                if ratio == 10:
                    st.warning(f"⚠️ 无法压缩到指定大小 {compress_size}M")
                    return
                pic_list = pdf_to_pic(uploaded_file.getvalue(), ratio)
                pdf_bits = pic_to_pdf(pic_list)
                ret_size = len(pdf_bits)
                ratio = ratio - 10
            
            if pdf_bits is None:
                st.error("❌ 压缩失败，请重试")
                return
            end = time()
            elapsed = end - start
            b64 = base64.b64encode(pdf_bits).decode('UTF-8')
            href = f'<a href="data:file/data;base64,{b64}" download="{uploaded_file.name}">📥 下载压缩文件 ({round(len(pdf_bits) / 1024 / 1024, 2)}M)</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success(f"✅ 压缩完成，耗时: {elapsed:.2f}s")
    else:
        st.info("💡 请上传PDF文件进行压缩")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传PDF**: 点击上方上传按钮，选择PDF文件
            2. **设置目标大小**: 滑动滑块设置压缩后的目标大小(1-20M)
            3. **操作流程**: 上传PDF → 设置目标大小 → 自动压缩 → 下载结果
            4. **注意事项**: 如果文件小于目标大小，则无需压缩
            """)


if __name__ == '__main__':
    main()

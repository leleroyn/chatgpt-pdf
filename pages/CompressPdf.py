from time import time

import streamlit as st

from service import *


def main():
    st.set_page_config(page_title="PDF压缩", layout="wide", menu_items={})
    st.subheader("🗜️PDF压缩")

    compress_size = st.slider('压缩到大小(单位M)', min_value=1, max_value=20, step=1, value=10)
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    if uploaded_file is not None:
        if compress_size is not None:
            with st.spinner("Please waiting..."):
                if len(uploaded_file.getvalue()) < compress_size * 1024 * 1024:
                    st.warning(
                        "上传的文件大小比设定的{compress_size}小，不需要压缩.".format(compress_size=compress_size))
                    return
                start = time()
                ret_size = len(uploaded_file.getvalue())
                ratio = 40
                while compress_size * 1024 * 1024 < ret_size:
                    if ratio == 10:
                        st.warning(
                            "无法压缩到指定的大小{compress_size}M.".format(compress_size=compress_size))
                        return
                    pic_list = pdf_to_pic(uploaded_file.getvalue(), ratio)
                    pdf_bits = pic_to_pdf(pic_list)
                    ret_size = len(pdf_bits)
                    ratio = ratio - 10
                st.info("当前ratio:" + ratio)
                end = time()
                elapsed = end - start
                b64 = base64.b64encode(pdf_bits).decode('UTF-8')  # 解码并加密为base64
                href = f'<a href="data:file/data;base64,{b64}" download="{uploaded_file.name}">下载压缩好的文件({round(len(pdf_bits) / 1024 / 1024, 2)}M)</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.info("压缩完成，共花费 {} 秒".format(elapsed))


if __name__ == '__main__':
    main()

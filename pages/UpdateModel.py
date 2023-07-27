import os

import docx
import filetype
import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from service import *


def main():
    faiss_path = "db/pd"
    faiss_index = "index"
    load_dotenv()

    st.set_page_config(page_title="人工智能", layout="wide", menu_items={})

    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
    font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader(":books:更新知识库")

    # 上传文件
    upload_files = st.file_uploader("上传文件", type=["pdf", "docx", "txt"], accept_multiple_files=True,
                                    help="不要频繁的更新知识库,不要上传大文件.")

    if st.button("更新模型↩️", key="update_model"):
        emt = st.empty()
        # 提取文本
        if len(upload_files) > 0:
            text = ""
            with st.spinner("正在更新模型..."):
                for upload_file in upload_files:
                    file_kind = filetype.guess_extension(upload_file) if filetype.guess_extension(
                        upload_file) is not None else "txt"
                    if file_kind == "pdf":
                        with pdfplumber.open(upload_file) as pdf_reader:
                            for page in pdf_reader.pages:
                                text += page.extract_text() + "\n"
                    elif file_kind == "docx":
                        docx_file = docx.Document(upload_file)
                        for para in docx_file.paragraphs:
                            text += para.text + "\n"
                    elif file_kind == "txt":
                        with upload_file as f:
                            for txt_bits in f.readlines():
                                try:
                                    txt_line = txt_bits.decode("utf-8")
                                except UnicodeDecodeError as e:
                                    txt_line = txt_bits.decode("gbk")
                                text += txt_line + "\n"
                    else:
                        emt.warning("不受支持的文件类型！", icon="⚠️")
                        st.stop()
                knowledge = KnowledgeService(faiss_path, faiss_index)
                knowledge.gen(text, os.getenv("SPLITTER_CHUCK_SIZE"), os.getenv("SPLITTER_CHUCK_OVER_LAP"))
            emt.success("✔️更新模型成功.")
            st.toast("更新模型成功.",icon="✔️")
        else:
            emt.warning("请上传模型文件.", icon="⚠️")
            st.stop()


if __name__ == '__main__':
    main()

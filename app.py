import os

import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from service import *


def main():
    chatgpt_model = "gpt-3.5-turbo"
    faiss_index = "index"

    load_dotenv()

    st.set_page_config(page_title="知识库")
    st.header("专属PDF知识库💬")
    kb_option_list = ("当前新版本", "历史版本")
    kb_option = st.selectbox("指定知识库模型", kb_option_list)

    if kb_option == "当前新版本":
        faiss_path = "db/pd"
    else:
        faiss_path = "db/sit"

    tab1, tab2 = st.tabs(["🏡回答问题", "🕝更新模型"])

    # 上传文件
    pdf = tab2.file_uploader("上传PDF文件", type="pdf", help="不要频繁的更新知识库,不要上传大文件.", key="pdf")

    if tab2.button("更新模型↩️"):
        tab2_emt = tab2.empty()
        # 提取文本
        if pdf is not None:
            tab2_emt.write("⏳正在更新模型...")
            text = ""
            with pdfplumber.open(pdf) as pdf_reader:
                for page in pdf_reader.pages:
                    text += page.extract_text()

            knowledge = KnowledgeService(faiss_path, faiss_index)
            knowledge.gen(text, os.getenv("SPLITTER_CHUCK_SIZE"), os.getenv("SPLITTER_CHUCK_OVER_LAP"))
            tab2_emt.success("✔️更新模型成功.")
        else:
            tab2_emt.warning("请上传模型文件.")

    user_question = st.chat_input("❓来向我提问吧：")
    if user_question:
        st_user = st.chat_message("user")
        st_user.write(user_question)
        st_emp = st.empty()
        st_emp.write("<p style=\"text-align: left;width:100%\">⏳ 正在思考中...</p>",unsafe_allow_html=True)
        knowledge = KnowledgeService(faiss_path, faiss_index)
        response, source_documents, cb = knowledge.query(chatgpt_model, user_question)
        st_assistant = st.chat_message("assistant")
        st_assistant.write(response)
        st_emp.empty()
        # st.info(source_documents)
        st.info(cb)


if __name__ == '__main__':
    main()

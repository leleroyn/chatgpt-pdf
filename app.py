import os

import docx
import filetype
import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from service import *
from service.ChatgptService import *


def main():
    chatgpt_model = "gpt-3.5-turbo"
    faiss_path = "db/pd"
    faiss_index = "index"
    load_dotenv()

    st.set_page_config(page_title="人工智能", layout="wide", menu_items={})

    # 用于保存历史对话
    ss_list = ["session_state_question", "session_state_answer"]
    for ss in ss_list:
        if ss not in st.session_state:
            st.session_state[ss] = []

    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
    font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.header("🏡Chatgpt人工智能体验")
    kb_option_list = (chatgpt_model, "自定义模型")
    kb_option = st.selectbox("指定知识库模型", kb_option_list)

    tab1, tab2 = st.tabs(["💬回答问题", "🕝更新自定义模型"])

    # 上传文件
    upload_files = tab2.file_uploader("上传文件", type=["pdf", "docx", "txt"], accept_multiple_files=True,
                                      help="不要频繁的更新知识库,不要上传大文件.")

    if tab2.button("更新模型↩️"):
        tab2_emt = tab2.empty()
        # 提取文本
        if upload_files is not None:
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
                        tab2_emt.warning("不受支持的文件类型！")
                        st.stop()
                knowledge = KnowledgeService(faiss_path, faiss_index)
                knowledge.gen(text, os.getenv("SPLITTER_CHUCK_SIZE"), os.getenv("SPLITTER_CHUCK_OVER_LAP"))
            tab2_emt.success("✔️更新模型成功.")
            st.toast("✔️更新模型成功.")
        else:
            tab2_emt.warning("请上传模型文件.")
            st.stop()

    if len(st.session_state["session_state_question"]) > 0:
        for index in range(len(st.session_state["session_state_question"])):
            st_odd_user = st.chat_message("user", avatar="🧑")
            st_odd_user.write(st.session_state["session_state_question"][index])
            st_odd_assistant = st.chat_message("assistant", avatar="🤖")
            st_odd_assistant.write(st.session_state["session_state_answer"][index])

    user_question = st.chat_input("❓来向我提问吧：")
    if user_question:
        st_user = st.chat_message("user", avatar="🧑")
        st_user.write(user_question)
        with st.spinner("正在思考中..."):
            if kb_option == chatgpt_model:
                chatgpt_service = ChatgptService(chatgpt_model)
                response, source_documents, cb = chatgpt_service.query(user_question, st.session_state[
                                                                                          "session_state_question"][
                                                                                      -5:],
                                                                       st.session_state[
                                                                           "session_state_answer"][-5:])
            else:
                knowledge = KnowledgeService(faiss_path, faiss_index)
                response, source_documents, cb = knowledge.query(chatgpt_model, user_question)

        st_odd_assistant = st.chat_message("assistant", avatar="🤖")
        st_odd_assistant.write(response)
        if source_documents is not None and len(source_documents) > 0:
            st.info(source_documents)
        st.info(cb)
        if response is not None and response.strip():
            st.session_state["session_state_question"].append(user_question)
            st.session_state["session_state_answer"].append(response)


if __name__ == '__main__':
    main()

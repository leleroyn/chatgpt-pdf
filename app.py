import os

import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from service import *
from service.ChatgptService import *


def main():
    chatgpt_model = "gpt-3.5-turbo"
    faiss_index = "index"
    load_dotenv()

    st.set_page_config(page_title="人工智能", menu_items={})

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
    kb_option_list = ("当前新版本", "历史版本")
    kb_option = st.selectbox("指定知识库模型", kb_option_list)

    if kb_option == "当前新版本":
        faiss_path = "db/pd"
    else:
        faiss_path = "db/sit"

    tab1, tab2 = st.tabs(["💬回答问题", "🕝更新模型"])

    # 上传文件
    pdf = tab2.file_uploader("上传PDF文件", type="pdf", help="不要频繁的更新知识库,不要上传大文件.", key="pdf")
    tab1_ck = tab1.checkbox("仅使用自定义模型")

    if tab2.button("更新模型↩️"):
        tab2_emt = tab2.empty()
        # 提取文本
        if pdf is not None:
            with st.spinner("正在更新模型..."):
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
        if len(st.session_state["session_state_question"]) > 0:
            for index in range(len(st.session_state["session_state_question"])):
                st_odd_user = st.chat_message("user", avatar="🧑")
                st_odd_user.write(st.session_state["session_state_question"][index])
                st_odd_assistant = st.chat_message("assistant", avatar="🤖")
                st_odd_assistant.write(st.session_state["session_state_answer"][index])

        st_user = st.chat_message("user", avatar="🧑")
        st_user.write(user_question)
        with st.spinner("正在思考中..."):
            if tab1_ck:
                knowledge = KnowledgeService(faiss_path, faiss_index)
                response, source_documents, cb = knowledge.query(chatgpt_model, user_question)
            else:
                chatgpt_service = ChatgptService(chatgpt_model)
                response, source_documents, cb = chatgpt_service.query(user_question, st.session_state[
                                                                                          "session_state_question"][
                                                                                      -5:],
                                                                       st.session_state[
                                                                           "session_state_answer"][-5:])
        st_assistant = st.chat_message("assistant", avatar="🤖")
        st_assistant.write(response)
        if source_documents is not None and len(source_documents) > 0:
            st.info(source_documents)
        st.info(cb)
        if response is not None and response.strip():
            st.session_state["session_state_question"].append(user_question)
            st.session_state["session_state_answer"].append(response)


if __name__ == '__main__':
    main()

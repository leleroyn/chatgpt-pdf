import streamlit as st
from dotenv import load_dotenv
from service import *
import streamlit.components.v1 as components


def main():
    chatgpt_model = "gpt-3.5-turbo"
    faiss_path = "db/pd"
    faiss_index = "index"
    load_dotenv()

    st.set_page_config(page_title="人工智能对话体验", layout="wide", menu_items={})

    # 用于保存历史对话
    ss_list = ["session_state_question", "session_state_answer"]
    for ss in ss_list:
        if ss not in st.session_state:
            st.session_state[ss] = []

    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
    font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("🏡人工智能对话体验")
    kb_option_list = (chatgpt_model, "自定义模型")
    kb_option = st.selectbox("指定知识库模型", kb_option_list)

    if len(st.session_state["session_state_question"]) > 0:
        for index in range(len(st.session_state["session_state_question"])):
            st_odd_user = st.chat_message("user", avatar="🧑")
            st_odd_user.write(st.session_state["session_state_question"][index])
            st_odd_assistant = st.chat_message("assistant", avatar="🤖")
            st_odd_assistant.write(st.session_state["session_state_answer"][index])

    user_question = st.chat_input("❓来向我提问吧：", key="user_question")
    if user_question:
        st_user = st.chat_message("user", avatar="🧑")
        st_user.write(user_question)
        if kb_option == chatgpt_model:
            with st.chat_message("assistant", avatar="🤖"):
                chatgpt_service = StreamChatgptService(chatgpt_model)
                response, source_documents, cb = chatgpt_service.query(user_question, st.session_state[
                                                                                          "session_state_question"][
                                                                                      -5:],
                                                                       st.session_state[
                                                                           "session_state_answer"][-5:], st.empty())
        else:
            knowledge = KnowledgeService(faiss_path, faiss_index)
            response, source_documents, cb = knowledge.query(chatgpt_model, user_question)

        if source_documents is not None and len(source_documents) > 0:
            st.info(source_documents)
        # st.info(cb)
        if response is not None and response.strip():
            st.session_state["session_state_question"].append(user_question)
            st.session_state["session_state_answer"].append(response)

    if st.session_state.user_question:
        components.html("<script type=\"text/javascript\">parent.document.querySelectorAll('[role=\"tab\"]')["
                        "0].click("
                        ")</script>")


if __name__ == '__main__':
    main()

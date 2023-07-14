import os

import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from service import KnowledgeService


def main():
    chatgpt_model = "gpt-3.5-turbo"
    candidate_number = 4
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

    tab1, tab2 = st.tabs(["回答问题", "更新模型"])

    # 上传文件
    pdf = tab2.file_uploader("上传PDF文件", type="pdf")
    # 提取文本
    if pdf is not None:
        with tab2.empty():
            st.write("⏳正在更新模型...")
            text = ""
            with pdfplumber.open(pdf) as pdf_reader:
                for page in pdf_reader.pages:
                    text += page.extract_text()

            knowledge = KnowledgeService(faiss_path, faiss_index)
            knowledge.gen(text, os.getenv("SPLITTER_CHUCK_SIZE"), os.getenv("SPLITTER_CHUCK_OVER_LAP"))

            st.success("✔️更新模型成功.")

    user_question = st.chat_input("❓来向我提问吧：")
    if user_question:
        user_question = f"已知信息:{user_question}\n请基于上面的已知信息准确回答,如果不知道,直接回答”根据已有信息暂时无法回答您的问题，请联系客服.“,请用中文回答."
        st_emt = st.empty()
        st_emt.write("⏳正在思考,请稍等...")
        knowledge = KnowledgeService(faiss_path, faiss_index)
        response, cb = knowledge.query(chatgpt_model, user_question, candidate_number)
        st_emt.write(response)
        st.info(cb)


if __name__ == '__main__':
    main()

import os

import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from service.KnowledgeService import KnowledgeService


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

    if st.checkbox("是否更新模型"):
        # 上传文件
        pdf = st.file_uploader("上传PDF文件", type="pdf")
        # 提取文本
        if pdf is not None:
            text = ""
            with pdfplumber.open(pdf) as pdf_reader:
                for page in pdf_reader.pages:
                    text += page.extract_text()

            knowledge = KnowledgeService(faiss_path, faiss_index)
            knowledge.gen(text, os.getenv("SPLITTER_CHUCK_SIZE"), os.getenv("SPLITTER_CHUCK_OVER_LAP"))

            st.success("更新模型成功.")
    else:
        user_question = st.text_input("来向我提问吧：")
        if user_question:
            knowledge = KnowledgeService(faiss_path, faiss_index)
            response, cb = knowledge.query(chatgpt_model, user_question, candidate_number)
            st.write(response)
            st.warning(cb)


if __name__ == '__main__':
    main()

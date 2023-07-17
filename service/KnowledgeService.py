from langchain import FAISS, PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re


class KnowledgeService(object):

    def __init__(self, faiss_path, index_name):
        self.faiss_path = faiss_path
        self.index_name = index_name

    def gen(self, text, chunk_size,chunk_overlap):
        # 文本分片
        docs = self.split_paragraph(text, int(chunk_size, 10),int(chunk_overlap, 10))
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(docs, embeddings)
        db.save_local(self.faiss_path, self.index_name)

    def query(self, model, user_question):
        knowledge_base = FAISS.load_local(folder_path=self.faiss_path, embeddings=OpenAIEmbeddings(),
                                          index_name=self.index_name)
        llm = ChatOpenAI(model_name=model, temperature=0)

        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know 
        the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer in Chinese:"""
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": prompt}
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                         retriever=knowledge_base.as_retriever(search_kwargs={"k": 3}),
                                         chain_type_kwargs=chain_type_kwargs, return_source_documents=True)

        # 如需追踪花了多少钱
        with get_openai_callback() as cb:
            # 回答的文本内容
            result = qa({"query": user_question})
            response = result["result"]
            # return_source_documents = True 才有这个参数
            source_documents = result["source_documents"]
            # source_documents = ""
        return response, source_documents, cb

    # 自定义句子分段的方式，保证句子不被截断
    def split_paragraph(self, text, chunk_size=300, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=20,
            length_function=len,
        )
        texts = text_splitter.create_documents([text])
        return texts
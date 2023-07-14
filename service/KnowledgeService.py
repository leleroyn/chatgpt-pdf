
from langchain import FAISS
from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter


class KnowledgeService:

    def __init__(self, faiss_path, index_name):
        self.faiss_path = faiss_path
        self.index_name = index_name

    def gen(self, text, chunk_size, chunk_overlap):
        # 文本分片
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=int(chunk_size, 10),
            chunk_overlap=int(chunk_overlap, 10),
            length_function=len
        )
        docs = text_splitter.split_text(text)
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_texts(docs, embeddings)
        db.save_local(self.faiss_path, self.index_name)

    def query(self, model, user_question, candidate_number):
        knowledge_base = FAISS.load_local(folder_path=self.faiss_path, embeddings=OpenAIEmbeddings(),
                                          index_name=self.index_name)
        docs = knowledge_base.similarity_search(user_question, candidate_number)
        llm = ChatOpenAI(model_name=model, temperature=0)
        chain = load_qa_chain(llm, chain_type="stuff")
        # 如需追踪花了多少钱
        with get_openai_callback() as cb:
            # 回答的文本内容
            response = chain.run(input_documents=docs, question=user_question)
        return response, cb

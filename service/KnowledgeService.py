from langchain import FAISS, PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import re


class KnowledgeService(object):

    def __init__(self, faiss_path, index_name):
        self.faiss_path = faiss_path
        self.index_name = index_name

    def gen(self, text, chunk_size):
        # 文本分片
        docs = self.split_paragraph(text, int(chunk_size, 10))
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_texts(docs, embeddings)
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
                                         retriever=knowledge_base.as_retriever(search_kwargs={"k": 10}),
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
    def split_paragraph(self, text, max_length=300):
        text = text.replace('\n', '')
        text = text.replace('\n\n', '')
        text = re.sub(r'\s+', ' ', text)
        """
        将文章分段
        """
        # 首先按照句子分割文章
        sentences = re.split(r'(|；|。|！|!|\.|？|\?)', text)

        new_sends = []
        for i in range(int(len(sentences) / 2)):
            sent = sentences[2 * i] + sentences[2 * i + 1]
            new_sends.append(sent)
        if len(sentences) % 2 == 1:
            new_sends.append(sentences[len(sentences) - 1])

        # 按照要求分段
        paragraphs = []
        current_length = 0
        current_paragraph = ""
        for sentence in new_sends:
            sentence_length = len(sentence)
            if current_length + sentence_length <= max_length:
                current_paragraph += sentence
                current_length += sentence_length
            else:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
                current_length = sentence_length
        paragraphs.append(current_paragraph.strip())
        return paragraphs

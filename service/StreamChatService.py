from langchain import PromptTemplate, LLMChain
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage

from service import StreamingLLMCallbackHandler


class StreamChatgptService:
    def __init__(self, model_name):
        self.model_name = model_name

    def query(self, user_question, session_state_question, session_state_answer, container):
        stream_handler = StreamingLLMCallbackHandler(container)
        llm = ChatOpenAI(model_name=self.model_name, temperature=0.7, streaming=True, callbacks=[stream_handler])

        chat_history = []
        for index in range(len(session_state_question)):
            chat_history.append("Human:" + session_state_question[index])
            chat_history.append("AI:" + session_state_answer[index])

        prompt = f"""You are a chatbot having a conversation with a human.

        {chat_history}
        Human: {user_question}
        AI:"""

        with get_openai_callback() as cb:
            llm([ChatMessage(role="user", content=prompt)])
            response = stream_handler.text
            source_documents = ""
        return response, source_documents, cb

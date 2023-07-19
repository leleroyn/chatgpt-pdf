from langchain import  PromptTemplate, LLMChain
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI

class ChatgptService:
    def __init__(self, model_name):
        self.model_name = model_name

    def query(self, user_question, session_state_question, session_state_answer):
        llm = ChatOpenAI(model_name=self.model_name, temperature=0.7)
        template = """You are a chatbot having a conversation with a human.

        {chat_history}
        Human: {human_input}
        AI:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"],
            template=template
        )

        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True
        )
        chat_history = []
        for index in range(len(session_state_question)):
            chat_history.append("Human:" + session_state_question[index])
            chat_history.append("AI:" + session_state_answer[index])

        with get_openai_callback() as cb:
            response = llm_chain.predict(human_input=user_question, chat_history="\n".join(chat_history))
            source_documents = ""
        return response, source_documents, cb

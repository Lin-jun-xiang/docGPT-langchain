import os
from abc import ABC, abstractmethod

import openai
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma

openai.api_key = os.getenv('OPENAI_API_KEY')


class BaseQaChain(ABC):
    def __init__(
        self,
        chain_type: str,
        retriever,
        llm
    ) -> None:
        self.chain_type = chain_type
        self.retriever = retriever
        self.llm = llm

    @abstractmethod
    def create_qa_chain(self):
        pass


class RChain(BaseQaChain):
    def __init__(
        self,
        chain_type: str,
        retriever,
        llm,
        chain_type_kwargs: dict
    ) -> None:
        super().__init__(chain_type, retriever, llm)
        self.chain_type_kwargs = chain_type_kwargs

    @property
    def create_qa_chain(self) -> RetrievalQA:
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=self.chain_type,
            retriever=self.retriever,
            chain_type_kwargs=self.chain_type_kwargs
        )
        return qa_chain


class CRChain(BaseQaChain):
    def __init__(
        self,
        chain_type: str,
        retriever,
        llm,
    ) -> None:
        super().__init__(chain_type, retriever, llm)

    @property
    def create_qa_chain(self) -> ConversationalRetrievalChain:
        # TODO: cannot use conversation qa chain
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            chain_type=self.chain_type,
            retriever=self.retriever,
            memory=memory
        )
        return qa_chain    


class DocGPT:
    def __init__(self, docs):
        self.docs = docs
        self.qa_chain = None
        self.llm = ChatOpenAI(
            temperature=0.2,
            max_tokens=6000,
            model_name='gpt-3.5-turbo-16k'
        )

        self.prompt_template = """
        Only answer what is asked. Answer step-by-step.
        If the content has sections, please summarize them in order and present them in a bulleted format.
        Utilize line breaks for better readability.
        For example, sequentially summarize the introduction, methods, results, and so on.

        {context}

        Question: {question}
        """

        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=['context', 'question']
        )

    def _helper_prompt(self, chain_type: str) -> None:
        # TODO: Bug helper
        if chain_type == 'refine':
            self.prompt_template = self.prompt_template.replace(
                '{context}', '{context_str}'
            )
            self.prompt.template = self.prompt_template
            for i in range(len(self.prompt.input_variables)):
                if self.prompt.input_variables[i] == 'context':
                    self.prompt.input_variables[i] = 'context_str'

    def _embeddings(self):
        embeddings = OpenAIEmbeddings()

        db = Chroma.from_documents(
            documents=self.docs,
            embedding= embeddings
        )

        return db

    def create_qa_chain(
        self,
        chain_type: str='stuff',
        chain_model: str='retrieval',
    ) -> BaseQaChain:
        db = self._embeddings()

        # TODO: Bug helper
        self._helper_prompt(chain_type)

        # TODO: Bug helper
        if chain_type in ('stuff', 'map_rerank'):
            chain_type_kwargs = {
                'prompt': self.prompt,
                'verbose': True
            }
        else:
            chain_type_kwargs = {
                'question_prompt': self.prompt,
                'verbose': True
            }

        retriever = db.as_retriever()

        if chain_model == 'retrieval':
            self.qa_chain = RChain(
                chain_type=chain_type,
                retriever=retriever,
                llm=self.llm,
                chain_type_kwargs=chain_type_kwargs
            ).create_qa_chain
        else:
            self.qa_chain = CRChain(
                chain_type=chain_type,
                retriever=retriever,
                llm=self.llm
            ).create_qa_chain

    def run(self, query: str) -> str:
        response = 'Nothing...'
        with get_openai_callback() as callback:
            if isinstance(self.qa_chain, RetrievalQA):
                response = self.qa_chain.run(query)
            elif isinstance(self.qa_chain, ConversationalRetrievalChain):
                chat_history = []
                response = self.qa_chain({'question': query, 'chat_history': chat_history})
            print(callback)
        return response

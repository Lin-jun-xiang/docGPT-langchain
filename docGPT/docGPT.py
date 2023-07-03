import logging
import os
from abc import ABC, abstractmethod

import openai
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma

from .prompt import SpecificationPromptor


openai.api_key = os.getenv('OPENAI_API_KEY')
# TODO: ADD logger
logger = logging.getLogger('./logs/openai_callback.log')


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
            llm=OpenAI(temperature=0),
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

    def _get_chat_history(self, inputs) -> str:
        res = []
        for human, ai in inputs:
            res.append(f"Human:{human}\nAI:{ai}")
        return "\n".join(res)

    @property
    def create_qa_chain(self) -> ConversationalRetrievalChain:
        # TODO: cannot use conversation qa chain
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=OpenAI(temperature=0),
            chain_type=self.chain_type,
            retriever=self.retriever,
            memory=memory,
            get_chat_history=self._get_chat_history
        )
        return qa_chain    


class DocGPT:
    def __init__(self, docs):
        self.docs = docs
        self.qa_chain = None

        self.prompt_template = """
        Cite each reference using [Page Number] notation (every result has this number at the beginning).
        Only answer what is asked. The answer should be short and concise. Answer step-by-step.

        {context}

        Question: {question}
        """

        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=['context', 'question']
        )

    def set_customer_prompt(self, promptor: str='specification') -> None:
        if promptor == 'specification':
            spec_prompt = SpecificationPromptor()
            self.prompt_template = spec_prompt.prompt_template
            self.prompt.template = self.prompt_template

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
                llm=OpenAI(temperature=0),
                chain_type_kwargs=chain_type_kwargs
            ).create_qa_chain
        else:
            self.qa_chain = CRChain(
                chain_type=chain_type,
                retriever=retriever,
                llm=OpenAI(temperature=0)
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

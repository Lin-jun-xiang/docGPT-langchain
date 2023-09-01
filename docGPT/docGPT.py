import os
from abc import ABC, abstractmethod
from typing import List, Optional

import g4f
import openai
from langchain.callbacks import get_openai_callback
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms.base import LLM
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS

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
        self._llm = None

        self.prompt_template = (
            "Only answer what is asked. Answer step-by-step.\n"
            "If the content has sections, please summarize them "
            "in order and present them in a bulleted format.\n"
            "Utilize line breaks for better readability.\n"
            "For example, sequentially summarize the "
            "introduction, methods, results, and so on.\n"
            "Please use Python's newline symbols appropriately to "
            "enhance the readability of the response, "
            "but don't use two newline symbols consecutive.\n\n"
            "{context}\n\n"
            "Question: {question}\n"
        )
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=['context', 'question']
        )

        self.refine_prompt_template = (
            "The original question is as follows: {question}\n"
            "We have provided an existing answer: {existing_answer}\n"
            "We have the opportunity to refine the existing answer"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{context_str}\n"
            "------------\n"
            "Given the new context, refine the original answer to better "
            "answer the question. "
            "If the context isn't useful, return the original answer.\n"
            "Please use Python's newline symbols "
            "appropriately to enhance the readability of the response, "
            "but don't use two newline symbols consecutive.\n"
        )
        self.refine_prompt = PromptTemplate(
            template=self.refine_prompt_template,
            input_variables=['question', 'existing_answer', 'context_str']
        )

    @property
    def llm(self):
        return self._llm

    @llm.setter
    def llm(self, llm) -> None:
        self._llm = llm

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
        try:
            # If have openai api
            embeddings = OpenAIEmbeddings()
        except:
            embeddings = HuggingFaceEmbeddings(
                model_name=(
                    'sentence-transformers/'
                    'multi-qa-MiniLM-L6-cos-v1'
                )
            )

        db = FAISS.from_documents(
            documents=self.docs,
            embedding=embeddings
        )
        print('embedded...')
        return db

    def create_qa_chain(
        self,
        chain_type: str='stuff',
    ) -> BaseQaChain:
        # TODO: Bug helper
        self._helper_prompt(chain_type)
        chain_type_kwargs = {
            'question_prompt': self.prompt,
            'verbose': True,
            'refine_prompt': self.refine_prompt
        }

        db = self._embeddings()
        retriever = db.as_retriever()

        self.qa_chain = RChain(
            chain_type=chain_type,
            retriever=retriever,
            llm=self._llm,
            chain_type_kwargs=chain_type_kwargs
        ).create_qa_chain

    def run(self, query: str) -> str:
        response = 'Nothing...'
        with get_openai_callback() as callback:
            if isinstance(self.qa_chain, RetrievalQA):
                response = self.qa_chain.run(query)
            print(callback)
        return response


class GPT4Free(LLM):
    PROVIDER_MAPPING = {
        'g4f.Provider.ChatgptAi': g4f.Provider.ChatgptAi,
        'g4f.Provider.AItianhu': g4f.Provider.AItianhu,
        'g4f.Provider.Acytoo': g4f.Provider.Acytoo,
        'g4f.Provider.AiService': g4f.Provider.AiService,
        'g4f.Provider.Aichat': g4f.Provider.Aichat,
        'g4f.Provider.Ails': g4f.Provider.Ails,
        'g4f.Provider.Bard': g4f.Provider.Bard,
        'g4f.Provider.Bing': g4f.Provider.Bing,
        'g4f.Provider.ChatgptLogin': g4f.Provider.ChatgptLogin,
        'g4f.Provider.DeepAi': g4f.Provider.DeepAi,
        'g4f.Provider.DfeHub': g4f.Provider.DfeHub,
        'g4f.Provider.EasyChat': g4f.Provider.EasyChat,
        'g4f.Provider.Forefront': g4f.Provider.Forefront,
        'g4f.Provider.GetGpt': g4f.Provider.GetGpt,
        'g4f.Provider.H2o': g4f.Provider.H2o,
        'g4f.Provider.Liaobots': g4f.Provider.Liaobots,
        'g4f.Provider.Lockchat': g4f.Provider.Lockchat,
        'g4f.Provider.Opchatgpts': g4f.Provider.Opchatgpts,
        'g4f.Provider.Raycast': g4f.Provider.Raycast,
        'g4f.Provider.Theb': g4f.Provider.Theb,
        'g4f.Provider.Vercel': g4f.Provider.Vercel,
        'g4f.Provider.Wewordle': g4f.Provider.Wewordle,
        'g4f.Provider.You': g4f.Provider.You,
        'g4f.Provider.Yqcloud': g4f.Provider.Yqcloud,
    }
    provider = PROVIDER_MAPPING['g4f.Provider.ChatgptAi']

    @property
    def _llm_type(self) -> str:
        return 'gpt4free model'

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        try:
            print('promopt: ', prompt)
            return g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                provider=self.provider
            )
        except Exception as e:
            print(f'{__file__}: {e}')

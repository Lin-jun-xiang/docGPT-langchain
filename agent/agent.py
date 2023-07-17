import os
from typing import Optional

import openai
from langchain import LLMMathChain, SerpAPIWrapper
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

openai.api_key = os.getenv('OPENAI_API_KEY')
os.environ['SERPAPI_API_KEY'] = os.getenv('SERPAPI_API_KEY')


class AgentHelper:
    """Add agent to help docGPT can be perfonm better."""
    def __init__(self) -> None:
        self.llm = OpenAI(temperature=0)
        self.agent_ = None
        self.tools = []

    @property
    def get_calculate_chain(self) -> Tool:
        llm_math_chain = LLMMathChain.from_llm(llm=self.llm, verbose=True)
        tool = Tool(
            name='Calculator',
            func=llm_math_chain.run,
            description='useful for when you need to answer questions about math'
        )
        return tool

    @property
    def get_searp_chain(self) -> Tool:

        search = SerpAPIWrapper()
        tool = Tool(
            name='Search',
            func=search.run,
            description='useful for when you need to answer questions about current events'
        )
        return tool

    def create_doc_chat(self, docGPT) -> Tool:
        """Add a custom docGPT tool"""
        tool = Tool(
            name='DocumentGPT',
            func=docGPT.run,
            description="""
            useful for when you need to answer questions from the context of PDF,
            """
        )
        return tool

    def create_llm_chain(self) -> Tool:
        """Add a llm tool"""
        prompt = PromptTemplate(
            input_variables = ['query'],
            template = '{query}'
        )
        llm_chain = LLMChain(llm=self.llm, prompt = prompt)

        tool = Tool(
            name='LLM',
            func=llm_chain.run,
            description='useful for general purpose queries and logic'
        )
        return tool

    def initialize(self, tools):
        for tool in tools:
            if isinstance(tool, Tool):
                self.tools.append(tool)

        self.agent_ = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def query(self, query: str) -> Optional[str]:
        response = None
        with get_openai_callback() as callback:
            # TODO: The true result will hide in 'Observation'
            # https://github.com/hwchase17/langchain/issues/4916
            # https://python.langchain.com/docs/modules/agents/how_to/intermediate_steps
            response = self.agent_.run(query)
            print(callback)
        return response

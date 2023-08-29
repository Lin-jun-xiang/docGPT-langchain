import os

import openai
import streamlit as st
from langchain.chat_models import ChatOpenAI
from streamlit import logger

from .agent import AgentHelper
from .check_api_key import OpenAiAPI, SerpAPI
from .docGPT import DocGPT, GPT4Free

openai.api_key = os.getenv('OPENAI_API_KEY')
os.environ['SERPAPI_API_KEY'] = os.getenv('SERPAPI_API_KEY')
module_logger = logger.get_logger(__name__)


def create_doc_gpt(docs):
    if not docs:
        return

    docGPT = DocGPT(docs=docs)

    try:
        if OpenAiAPI.is_valid():
            # Use openai llm model with agent
            docGPT_tool, calculate_tool, search_tool, llm_tool = [None] * 4
            agent_ = AgentHelper()

            llm_model = ChatOpenAI(
                temperature=0.2,
                max_tokens=6000,
                model_name='gpt-3.5-turbo-16k'
            )
            docGPT.llm = llm_model
            agent_.llm = llm_model
            with st.spinner('Running...'):
                docGPT.create_qa_chain(
                    chain_type='refine',
                )
            docGPT_tool = agent_.create_doc_chat(docGPT)
            calculate_tool = agent_.get_calculate_chain
            llm_tool = agent_.create_llm_chain()

            if SerpAPI.is_valid():
                search_tool = agent_.get_searp_chain

                tools = [
                    docGPT_tool,
                    search_tool,
                    # llm_tool, # This will cause agent confuse
                    calculate_tool
                ]
                agent_.initialize(tools)
                return agent_ if agent_ is not None else None
            else:
                return docGPT
        else:
            # Use gpt4free llm model without agent
            llm_model = GPT4Free(
                provider=GPT4Free().PROVIDER_MAPPING[
                    st.session_state.g4f_provider
                ]
            )
            docGPT.llm = llm_model
            with st.spinner('Running...(free model will take more time)'):
                docGPT.create_qa_chain(
                    chain_type='refine',
                )
            return docGPT
    except Exception as e:
        module_logger.info(f'{__file__}: {e}')

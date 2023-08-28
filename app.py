import os
import tempfile
from functools import lru_cache

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SERPAPI_API_KEY'] = ''

import langchain
import streamlit as st
from langchain.cache import InMemoryCache
from langchain.chat_models import ChatOpenAI
from streamlit import logger
from streamlit_chat import message

from agent import AgentHelper
from docGPT import DocGPT, OpenAiAPI, SerpAPI, GPT4Free
from model import PDFLoader
import g4f
from tenacity import retry, stop_after_attempt

langchain.llm_cache = InMemoryCache()

OPENAI_API_KEY = ''
SERPAPI_API_KEY = ''
agent_ = None

st.session_state.openai_api_key = None
st.session_state.serpapi_api_key = None
st.session_state.g4f_provider = None
app_logger = logger.get_logger(__name__)


def theme():
    st.set_page_config(page_title="DocGPT")
    icon, title = st.columns([3, 20])
    with icon:
        st.image('./img/chatbot.png')
    with title:
        st.title('PDF Chatbot')


def load_api_key() -> None:
    with st.sidebar:
        if st.session_state.openai_api_key:
            OPENAI_API_KEY = st.session_state.openai_api_key
            st.sidebar.success('API key loaded form previous input')
        else:
            OPENAI_API_KEY = st.sidebar.text_input(
                label='#### Your OpenAI API Key 👇',
                placeholder="sk-...",
                type="password",
                key='OPENAI_API_KEY'
            )
            st.session_state.openai_api_key = OPENAI_API_KEY

        os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    with st.sidebar:
        if st.session_state.serpapi_api_key:
            SERPAPI_API_KEY = st.session_state.serpapi_api_key
            st.sidebar.success('API key loaded form previous input')
        else:
            SERPAPI_API_KEY = st.sidebar.text_input(
                label='#### Your SERPAPI API Key 👇',
                placeholder="...",
                type="password",
                key='SERPAPI_API_KEY'
            )
            st.session_state.serpapi_api_key = SERPAPI_API_KEY

        os.environ['SERPAPI_API_KEY'] = SERPAPI_API_KEY

    with st.sidebar:
        st.session_state.g4f_provider = st.selectbox(
            (
                "#### Select a provider if you want to use free model. "
                "([details](https://github.com/xtekky/gpt4free#models))"
            ),
            (GPT4Free().PROVIDER_MAPPING.keys())
        )


def upload_and_process_pdf():
    upload_file = st.file_uploader('#### Upload a PDF file:', type='pdf')
    if upload_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(upload_file.read())
        temp_file_path = temp_file.name

        docs = PDFLoader.load_documents(temp_file_path)
        docs = PDFLoader.split_documents(docs, chunk_size=2000, chunk_overlap=200)

        temp_file.close()
        if temp_file_path:
            os.remove(temp_file_path)

        return docs


@lru_cache(maxsize=20)
def get_response(query: str):
    try:
        if agent_.agent_ is not None:
            response = agent_.query(query)
            return response
    except Exception as e:
        app_logger.info(e)


theme()
load_api_key()

doc_container = st.container()


with doc_container:
    docs = upload_and_process_pdf()

    if docs:
        docGPT = DocGPT(docs=docs)
        docGPT_tool, calculate_tool, search_tool, llm_tool = [None]*4
        agent_ = AgentHelper()

        if OpenAiAPI.is_valid():
            # Use openai llm model
            docGPT.llm = ChatOpenAI(
                temperature=0.2,
                max_tokens=6000,
                model_name='gpt-3.5-turbo-16k'
            )
            agent_.llm = ChatOpenAI(
                temperature=0.2,
                max_tokens=6000,
                model_name='gpt-3.5-turbo-16k'
            )
            docGPT.create_qa_chain(
                chain_type='refine',
            )

            docGPT_tool = agent_.create_doc_chat(docGPT)
            calculate_tool = agent_.get_calculate_chain
            llm_tool = agent_.create_llm_chain()

            if SerpAPI.is_valid():
                search_tool = agent_.get_searp_chain
        else:
            # Use gpt4free llm model
            docGPT.llm = GPT4Free(
                provider=GPT4Free().PROVIDER_MAPPING[
                    st.session_state.g4f_provider
                ]
            )
            agent_.llm = GPT4Free(
                provider=GPT4Free().PROVIDER_MAPPING[
                    st.session_state.g4f_provider
                ]
            )
            docGPT.create_qa_chain(
                chain_type='refine',
            )
            docGPT_tool = agent_.create_doc_chat(docGPT)
        try:
            tools = [
                docGPT_tool,
                search_tool,
                # llm_tool, # This will cause agent confuse
                calculate_tool
            ]
            agent_.initialize(tools)
        except Exception as e:
            app_logger.info(e)


    st.write('---')

if 'response' not in st.session_state:
    st.session_state['response'] = ['How can I help you?']

if 'query' not in st.session_state:
    st.session_state['query'] = ['Hi']

user_container = st.container()
response_container = st.container()

with user_container:
    query = st.text_input(
        "#### Question:",
        placeholder='Enter your question'
    )

    if query and query != '':
        response = get_response(query)
        st.session_state.query.append(query)
        st.session_state.response.append(response) 

with response_container:
    if st.session_state['response']:
        for i in range(len(st.session_state['response'])-1, -1, -1):
            message(
                st.session_state["response"][i], key=str(i),
                logo=(
                    'https://api.dicebear.com/6.x/bottts/svg?'
                    'baseColor=fb8c00&eyes=bulging'
                )    
            )
            message(
                st.session_state['query'][i], is_user=True, key=str(i) + '_user',
                logo=(
                    'https://api.dicebear.com/6.x/adventurer/svg?'
                    'hair=short16&hairColor=85c2c6&'
                    'eyes=variant12&size=100&'
                    'mouth=variant26&skinColor=f2d3b1'
                )
            )

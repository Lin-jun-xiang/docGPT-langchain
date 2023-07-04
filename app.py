import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SERPAPI_API_KEY'] = ''

import tempfile

import langchain
import streamlit as st
from langchain.cache import InMemoryCache

from agent import AgentHelper
from docGPT import DocGPT
from model import PDFLoader


langchain.llm_cache = InMemoryCache()

OPENAI_API_KEY = ''
SERPAPI_API_KEY = ''
agent_ = None

st.session_state.openai_api_key = None
st.session_state.serpapi_api_key = None


def theme():
    st.set_page_config(page_title="DocGPT")

    icon, title = st.columns([3, 20])
    with icon:
        st.image('./img/chatbot.png')
    with title:
        st.title('PDF Chatbot')


theme()


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
            st.session_state.serpai_api_key = SERPAPI_API_KEY

        os.environ['SERPAPI_API_KEY'] = SERPAPI_API_KEY


load_api_key()


with st.container():
    upload_file = st.file_uploader('#### Upload a PDF file:', type='pdf')
    if upload_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(upload_file.read())
        temp_file_path = temp_file.name

        docs = PDFLoader.load_documents(temp_file_path)
        docs = PDFLoader.split_documents(docs, chunk_size=2500, chunk_overlap=200)

        temp_file.close()
        if temp_file_path:
            os.remove(temp_file_path)

        docGPT, docGPT_spec, calculate_tool, search_tool = None, None, None, None

        try:
            agent_ = AgentHelper()
            docGPT = DocGPT(docs=docs)
            docGPT.create_qa_chain(
                chain_type='refine',
            )
            docGPT_tool = agent_.create_doc_chat(docGPT)

            docGPT_spec = DocGPT(docs=docs)
            docGPT_spec.create_qa_chain(
                chain_type='refine',
            )
            docGPT_spec_tool = agent_.create_doc_chat(docGPT_spec)
        except Exception:
            st.error('#### ⚠️ :red[You have not pass OpenAPI key. (Or your api key cannot use.)]')
            
        try:
            search_tool = agent_.get_searp_chain
        except Exception as e:
            st.warning('⚠️ You have not pass SEARPAPI key. (Or your api key cannot use.) Try Refresh')

        try:
            calculate_tool = agent_.get_calculate_chain

            tools = [
                docGPT_tool, docGPT_spec_tool,
                calculate_tool, search_tool
            ]
            agent_.initialize(tools)
        except Exception:
            pass

st.write('---')

with st.container():
    query = st.text_input('#### Question:')
    response = None

    if agent_ and query and query != '':
            response = 'loading...'
            response = agent_.query(query)

    st.write('### :blue[Response]:')
    st.write(response)

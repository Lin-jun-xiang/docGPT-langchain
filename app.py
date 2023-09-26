import os
import tempfile

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SERPAPI_API_KEY'] = ''

import langchain
import streamlit as st
from langchain.cache import InMemoryCache
from streamlit import logger
from streamlit_chat import message

from docGPT import GPT4Free, create_doc_gpt
from model import DocumentLoader

langchain.llm_cache = InMemoryCache()

OPENAI_API_KEY = ''
SERPAPI_API_KEY = ''
model = None

st.session_state.openai_api_key = None
st.session_state.serpapi_api_key = None
st.session_state.g4f_provider = None
st.session_state.button_clicked = None


if 'response' not in st.session_state:
    st.session_state['response'] = ['How can I help you?']

if 'query' not in st.session_state:
    st.session_state['query'] = ['Hi']

app_logger = logger.get_logger(__name__)


def theme() -> None:
    st.set_page_config(page_title="Document GPT")
    st.image('./static/img/repos_logo.png', width=250)

    with st.sidebar:

        with st.expander(':orange[How to use?]'):
            st.markdown(
                """
                1. Enter your API keys: (You can choose to skip it and use the `gpt4free` free model)
                    * `OpenAI API Key`: Make sure you still have usage left
                    * `SERPAPI API Key`: Optional. If you want to ask questions about content not appearing in the PDF document, you need this key.
                2. Upload a Document file (choose one method):
                    * method1: Browse and upload your own `.pdf or .docx` file from your local machine.
                    * method2: Enter the PDF or DOCX `URL` link directly.
                3. Start asking questions!
                4. More details.(https://github.com/Lin-jun-xiang/docGPT-streamlit)
                5. If you have any questions, feel free to leave comments and engage in discussions.(https://github.com/Lin-jun-xiang/docGPT-streamlit/issues)
                """
            )


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
            (GPT4Free().providers_table.keys())
        )

        st.session_state.button_clicked = st.button(
            'Show Available Providers',
            help='Click to test which providers are currently available.',
            type='primary'
        )
        if st.session_state.button_clicked:
            available_providers = GPT4Free().find_available_providers()
            st.session_state.query.append('What are the available providers right now?')
            st.session_state.response.append(
                'The current available providers are:\n'
                f'{available_providers}'
            )


def upload_and_process_document() -> list:
    st.write('#### Upload a Document file')
    browse, url_link = st.tabs(
        ['Drag and drop file (Browse files)', 'Enter document URL link']
    )
    with browse:
        upload_file = st.file_uploader(
            'Browse file (.pdf, .docx)',
            type=['pdf', 'docx'],
            label_visibility='hidden'
        )
        filetype = os.path.splitext(upload_file.name)[1].lower()
        upload_file = upload_file.read() if upload_file else None

    with url_link:
        doc_url = st.text_input(
            "Enter document URL Link (.pdf, .docx)",
            placeholder='https://www.xxx/uploads/file.pdf',
            label_visibility='hidden'
        )
        if doc_url:
            upload_file, filetype = DocumentLoader.crawl_file(doc_url)

    if upload_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(upload_file)
        temp_file_path = temp_file.name

        docs = DocumentLoader.load_documents(temp_file_path, filetype)
        docs = DocumentLoader.split_documents(
            docs, chunk_size=2000,
            chunk_overlap=200
        )

        temp_file.close()
        if temp_file_path:
            os.remove(temp_file_path)

        return docs


def get_response(query: str) -> str:
    app_logger.info(f'\033[36mUser Query: {query}\033[0m')
    try:
        if model is not None and query:
            response = model.run(query)
            app_logger.info(f'\033[36mLLM Response: {response}\033[0m')
            return response
        return (
            'Your model still not created.\n'
            '1. If you are using gpt4free model, '
            'try to re-select a provider. '
            '(Click the "Show Available Providers" button in sidebar)\n'
            '2. If you are using openai model, '
            'try to re-pass openai api key.\n'
            '3. Or you did not pass the PDF file successfully.'
        )
    except Exception as e:
        app_logger.info(f'{__file__}: {e}')
        return (
            'Something wrong in docGPT...\n'
            '1. If you are using gpt4free model, '
            'try to select the different provider. '
            '(Click the "Show Available Providers" button in sidebar)\n'
            '2. If you are using openai model, '
            'check your usage for openai api key.'
        )


theme()
load_api_key()

doc_container = st.container()

with doc_container:
    docs = upload_and_process_document()

    if docs:
        model = create_doc_gpt(
            docs,
            {k: v for k, v in docs[0].metadata.items() if k not in ['source', 'file_path']},
            st.session_state.g4f_provider
        )
        app_logger.info(f'{__file__}: Created model: {model}')
        del docs
    st.write('---')

user_container = st.container()
response_container = st.container()

with user_container:
    query = st.text_input(
        "#### Question:",
        placeholder='Enter your question'
    )

    if query and query != '' and not st.session_state.button_clicked:
        response = get_response(query)
        st.session_state.query.append(query)
        st.session_state.response.append(response) 

with response_container:
    if st.session_state['response']:
        for i in range(len(st.session_state['response'])-1, -1, -1):
            message(
                st.session_state["response"][i], key=str(i),
                logo=(
                    'https://github.com/Lin-jun-xiang/docGPT-streamlit/'
                    'blob/main/static/img/chatbot_v2.png?raw=true'
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

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SERPAPI_API_KEY'] = ''

import streamlit as st
from streamlit import logger
from streamlit_chat import message

from components import get_response, load_api_key, theme, upload_and_process_document
from docGPT import create_doc_gpt

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


def main():
    global model
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

        if model and query and query != '' and not st.session_state.button_clicked:
            response = get_response(query, model)
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


if __name__ == "__main__":
    main()

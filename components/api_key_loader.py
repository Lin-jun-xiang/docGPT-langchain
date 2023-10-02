import asyncio
import os

import streamlit as st

from docGPT import GPT4Free


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
        gpt4free = GPT4Free()
        st.session_state.g4f_provider = st.selectbox(
            (
                "#### Select a provider if you want to use free model. "
                "([details](https://github.com/xtekky/gpt4free#models))"
            ),
            (gpt4free.providers_table.keys())
        )

        st.session_state.button_clicked = st.button(
            'Show Available Providers',
            help='Click to test which providers are currently available.',
            type='primary'
        )
        if st.session_state.button_clicked:
            available_providers = asyncio.run(gpt4free.show_available_providers())
            st.session_state.query.append('What are the available providers right now?')
            st.session_state.response.append(
                'The current available providers are:\n'
                f'{available_providers}'
            )

import streamlit as st


def theme() -> None:
    st.set_page_config(page_title="Document GPT")
    st.image('./static/img/repos_logo.png', width=250)

    with st.sidebar:
        with st.expander(':orange[How to use?]'):
            st.markdown(
                """
                1. Enter your API keys: (You can use the `gpt4free` free model **without API keys**)
                    * `OpenAI API Key`: Make sure you still have usage left
                    * `SERPAPI API Key`: Optional. If you want to ask questions about content not appearing in the PDF document, you need this key.
                2. **Upload a Document** file (choose one method):
                    * method1: Browse and upload your own document file from your local machine.
                    * method2: Enter the document URL link directly.
                    
                    (**support documents**: `.pdf`, `.docx`, `.csv`, `.txt`)
                3. Start asking questions!
                4. More details.(https://github.com/Lin-jun-xiang/docGPT-streamlit)
                5. If you have any questions, feel free to leave comments and engage in discussions.(https://github.com/Lin-jun-xiang/docGPT-streamlit/issues)
                """
            )

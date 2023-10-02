import os
import tempfile

import streamlit as st

from model import DocumentLoader


def upload_and_process_document() -> list:
    st.write('#### Upload a Document file')
    browse, url_link = st.tabs(
        ['Drag and drop file (Browse files)', 'Enter document URL link']
    )
    with browse:
        upload_file = st.file_uploader(
            'Browse file (.pdf, .docx, .csv, `.txt`)',
            type=['pdf', 'docx', 'csv', 'txt'],
            label_visibility='hidden'
        )
        filetype = os.path.splitext(upload_file.name)[1].lower() if upload_file else None
        upload_file = upload_file.read() if upload_file else None

    with url_link:
        doc_url = st.text_input(
            "Enter document URL Link (.pdf, .docx, .csv, .txt)",
            placeholder='https://www.xxx/uploads/file.pdf',
            label_visibility='hidden'
        )
        if doc_url:
            upload_file, filetype = DocumentLoader.crawl_file(doc_url)

    if upload_file and filetype:
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

import os
from typing import Iterator, Union

import requests
import streamlit as st
from langchain.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentLoader:
    @staticmethod
    def get_files(path: str, filetype: str = '.pdf') -> Iterator[str]:
        try:
            yield from [
                file_name for file_name in os.listdir(f'{path}')
                if file_name.endswith(filetype)
            ]
        except FileNotFoundError as e:
            print(f'\033[31m{e}')

    @staticmethod
    def load_documents(
        file: str,
        filetype: str = '.pdf'
    ) -> Union[CSVLoader, Docx2txtLoader, PyMuPDFLoader, TextLoader]:
        """Loading PDF, Docx, CSV"""
        try:
            if filetype == '.pdf':
                loader = PyMuPDFLoader(file)
            elif filetype == '.docx':
                loader = Docx2txtLoader(file)
            elif filetype == '.csv':
                loader = CSVLoader(file, encoding='utf-8')
            elif filetype == '.txt':
                loader = TextLoader(file, encoding='utf-8')

            return loader.load()

        except Exception as e:
            print(f'\033[31m{e}')
            return []

    @staticmethod
    def split_documents(
        document: Union[CSVLoader, Docx2txtLoader, PyMuPDFLoader, TextLoader],
        chunk_size: int=2000,
        chunk_overlap: int=0
    ) -> list:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        return splitter.split_documents(document)

    @staticmethod
    def crawl_file(url: str) -> str:
        try:
            response = requests.get(url)
            filetype = os.path.splitext(url)[1]
            if response.status_code == 200 and (
                '.pdf' in filetype or '.docx' in filetype):
                return response.content, filetype
            else:
                st.warning('Url cannot parse correctly.')
        except:
            st.warning('Url cannot parse correctly.')

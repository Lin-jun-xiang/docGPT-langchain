import json
import os
from typing import Iterator

from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFLoader:
    @staticmethod
    def get_pdf_files(path: str) -> Iterator[str]:
        try:
            yield from [
                file_name for file_name in os.listdir(f'{path}')
                if file_name.endswith('.pdf')
            ]
        except FileNotFoundError as e:
            print(f'\033[31m{e}')

    @staticmethod
    def load_documents(pdf_file: str) -> PyMuPDFLoader:
        """Loading and separating each page of a PDF"""
        loader = PyMuPDFLoader(f'{pdf_file}')
        return loader.load()

    @staticmethod
    def split_documents(
        document: PyMuPDFLoader,
        chunk_size: int=2000,
        chunk_overlap: int=0
    ) -> list:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        return splitter.split_documents(document)

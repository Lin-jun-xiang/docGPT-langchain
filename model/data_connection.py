import json
import os

from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFLoader:
    @staticmethod
    def get_pdf_files(path: str) -> list:
        if path.endswith('.pdf'):
            return f'./PDF/uploaded/{path}'
    
        else:
                file_names = os.listdir(f'./PDF/{path}')
                pdf_files = [name for name in file_names if name.endswith('.pdf')]

        return pdf_files

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


class JSONWriter:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
    
    def writer(self, data: list) -> None:
        if os.path.exists(self.file_name):
            with open(self.file_name) as file:
                listObj = json.load(file)

            listObj.extend(data)
            data = listObj

        with open(self.file_name, 'w') as file:
            json.dump(
                data,
                file, 
                indent=4
            )


class LoggerHandle:
    def qa_chain(self, chain_type: str, retriever, llm):
        pass
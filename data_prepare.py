

from typing import List, Optional
from langchain.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from config import *


def load_data_split(data_dir: Optional[str], chunk_size: Optional[int], chunk_overlap: Optional[int]):
    """
    Load and split the data
    :param data_dir:
    :param chunk_size:
    :param chunk_overlap:
    :return:
    """
    # Load and process the data
    if data_dir is None:
        data_dir = Cfg.DATA_DIR
    data_loader = DirectoryLoader(data_dir, glob="*.PDF")
    documents = data_loader.load()
    print("number of documents:", len(documents))

    if chunk_size is None:
        chunk_size = Cfg.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = Cfg.CHUNK_OVERLAP
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print("number of documents splitted:", len(texts))

    return texts


def load_data(texts: List[str], persist_dir: Optional[str], sub_dir: str):
    """
    embedding the texts and store them into a vector database
    :param texts:
    :param persist_dir:
    :param sub_dir:
    :return:
    """
    if persist_dir is None:
        persist_dir = Cfg.PERSIST_DIR
    persist_directory = os.path.join(persist_dir, sub_dir)

    # Embed the texts
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    vectordb.persist()

    return vectordb


def add_data(texts: List[str], persist_dir: Optional[str], sub_dir: str):
    """
    embedding the texts and store them into a vector database
    :param texts:
    :param persist_dir:
    :param sub_dir:
    :return:
    """
    if persist_dir is None:
        persist_dir = Cfg.PERSIST_DIR
    persist_directory = os.path.join(persist_dir, sub_dir)

    # Embed the texts
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    vectordb.add_documents(texts)

    vectordb.persist()

    return vectordb


def main():
    """
    1. 读取文档或者文件夹下的文档
    2. 对文档进行切块
    3. 对文档块进行embedding
    4. 存储到向量数据库
    5. 允许增量更新
    6. 允许多个主题（多个表或者文件存储路径）
    :return:
    """
    texts = load_data_split(data_dir=Cfg.DATA_DIR, chunk_size=Cfg.CHUNK_SIZE, chunk_overlap=Cfg.CHUNK_OVERLAP)
    vectordb = load_data(texts=texts, persist_dir=Cfg.PERSIST_DIR, sub_dir="strategy")

    print("embedding data success !")


if __name__ == "__main__":
   main()
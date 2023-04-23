

# 使用LangChain的ConversationalRetrievalChain，对Chroma向量数据库中的向量进行检索，返回最相似的向量，然后回答query问题
# 使用flask框架，将检索到的答案返回给前端

import sys

sys.path.append("..")


from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT
from langchain.chains.question_answering import load_qa_chain
from typing import List, Optional
from google_translation import GoogleTranslation
from config import *


gtranslate = GoogleTranslation()
embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

# 翻译
def translate(text: str, target_lang: str = "zh-CN", source_lang: str = "en"):
    return gtranslate.google_translate(text, target_lang, source_lang)


# 选择使用的向量数据库路径 category
def select_vectorstore(persist_dir: Optional[str], sub_dir: str):
    if persist_dir is None:
        persist_dir = Cfg.PERSIST_DIR

    persist_directory = os.path.join(persist_dir, sub_dir)
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    return vectorstore


def init_conver_qa_chain(vectorstore: Chroma):
    # qa = ConversationalRetrievalChain.from_llm(
    #     OpenAI(temperature=0, verbose=True),
    #     vectorstore.as_retriever(),
    #     verbose=True,
    # )

    question_gen_llm = OpenAI(
        temperature=0,
        verbose=True,
    )
    streaming_llm = OpenAI(
        verbose=True,
        temperature=0,
    )

    question_generator = LLMChain(
        llm=question_gen_llm, prompt=Cfg.CONDENSE_QUESTION_PROMPT
    )
    doc_chain = load_qa_chain(
        streaming_llm, chain_type="stuff", prompt=Cfg.QA_PROMPT
    )

    qa_chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
    )

    return qa_chain


def init_conver_qa_chain_stream(vectorstore: Chroma):

    llm = OpenAI(temperature=0)
    streaming_llm = OpenAI(streaming=True,
                           callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                           verbose=True,
                           temperature=0)
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_chain(streaming_llm, chain_type="stuff", prompt=QA_PROMPT)
    qa_chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator
    )

    return qa_chain


def prompt_select():
    pass


def conversation_qa(query: str, chat_history: List[str], category: str, stream: bool = False):

    query_source = query
    query = gtranslate.translate(query, to_language="en", text_language="zh-CN")

    chat_history = [
        (gtranslate.translate(text[0], to_language="en", text_language="zh-CN"),
         gtranslate.translate(text[1], to_language="en", text_language="zh-CN")) for text in chat_history
    ]

    print("-- query:", query)
    print("-- chat_history:", chat_history)
    print("-- category:", category)
    print("-- stream:", stream)

    if category not in Cfg.category_mapping_dict:
        return "category not found"

    sud_dir = Cfg.category_mapping_dict[category]

    vectorstore = select_vectorstore(persist_dir=Cfg.PERSIST_DIR, sub_dir=sud_dir)
    if stream:
        qa_chain = init_conver_qa_chain_stream(vectorstore)
        # result = qa_chain({"question": query, "chat_history": chat_history})
    else:
        qa_chain = init_conver_qa_chain(vectorstore)
        # result = qa_chain({"question": query, "chat_history": chat_history})
    result = qa_chain({"question": query, "chat_history": chat_history})

    result["answer"] = translate(result["answer"], target_lang="zh-CN", source_lang="en")
    result["question"] = translate(query_source, target_lang="zh-CN", source_lang="en")

    return result


if __name__ == "__main__":
    query = "How many people are in the Iran army?"
    chat_history = []
    category = "strategy"
    res = conversation_qa(query, chat_history, category)
    print(res)




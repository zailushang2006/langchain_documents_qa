

import os
os.environ["OPENAI_API_KEY"] = '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'


from langchain.prompts import PromptTemplate


class Cfg():
    DATA_DIR = "data/strategy"
    PERSIST_DIR = "database"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 0

    category_mapping_dict = {
        "strategy": "strategy",
    }

    _template = """鉴于以下对话和后续问题，将后续问题改写为独立问题。结果为简体中文，如何是非中文，则进行翻译。

    聊天历史:
    {chat_history}
    跟进输入: {question}
    独立问题:"""
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    prompt_template = """最后使用以下上下文来回答问题。如果你不知道答案，就说你不知道，不要试图编造答案。结果为简体中文，如何是非中文，则进行翻译。

    {context}

    问题: {question}
    有用的答案:"""
    QA_PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    SERVER_PORT = 15001

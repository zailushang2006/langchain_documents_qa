"""Main entrypoint for the app."""
import json
import logging
import pickle
from pathlib import Path
from typing import Optional, Dict

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain.vectorstores import VectorStore, Chroma
from langchain.embeddings import OpenAIEmbeddings

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from query_data import get_chain
from schemas import ChatResponse
from google_translation import GoogleTranslation
from config import *

gtranslate = GoogleTranslation()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
vectorstore: Optional[VectorStore] = None
category_name: str = "strategy"
vectorstore_dict: Optional[Dict[str, VectorStore]] = None


# @app.on_event("startup")
# async def startup_event():
#     logging.info("loading vectorstore")
#     if not Path("vectorstore.pkl").exists():
#         raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
#     with open("vectorstore.pkl", "rb") as f:
#         global vectorstore
#         vectorstore = pickle.load(f)


@app.on_event("startup")
async def startup_event():
    logging.info("loading vectorstore")
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    global vectorstore_dict
    vectorstore_dict = {}
    for sub_dir in os.listdir(Cfg.PERSIST_DIR):
        print("-- sub_dir -- ", sub_dir)
        persist_directory = os.path.join(Cfg.PERSIST_DIR, sub_dir)
        if os.path.isdir(persist_directory):
            print("-- persist_directory -- ", persist_directory)
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
            vectorstore_dict[sub_dir] = vectorstore
    print("-- vectorstore_dict -- ", vectorstore_dict)


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/documents_qa")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    chat_history = []

    qa_chain = get_chain(vectorstore_dict[category_name], question_handler, stream_handler)
    # Use the below line instead of the above line to enable tracing
    # Ensure `langchain-server` is running
    # qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)

    while True:
        try:
            # Receive and send back the client message
            # question = await websocket.receive_text()

            data = await websocket.receive_json()
            if isinstance(data, str):
                data = json.loads(data)
            print("-- data -- ", data)
            question = data['query']
            print("-- question -- ", question)
            question = gtranslate.translate(question, to_language="en", text_language="zh-CN")

            # 发送用户信息
            resp = ChatResponse(sender="you", message=question, type="stream")
            print("-- resp -- ", resp.dict())
            await websocket.send_json(resp.dict())

            # 发送开始信息
            start_resp = ChatResponse(sender="bot", message="", type="start")
            print("-- start_resp -- ", start_resp)
            await websocket.send_json(start_resp.dict())

            # 获取合适的向量数据库
            qa_chain.retriever = vectorstore_dict[data.get('category', "trategy")].as_retriever()

            # 发送答案信息
            result = await qa_chain.acall(
                {"question": question, "chat_history": chat_history}
            )
            print("-- result -- ", result)
            answer = result["answer"]
            print("-- answer -- ", answer)
            answer = gtranslate.translate(answer, to_language="en", text_language="zh-CN")
            print("-- tranlate answer -- ", answer)
            chat_history.append((question, answer))

            # 发送结束信息
            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())

        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error("-- error info --: %s", e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.dict())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=Cfg.SERVER_PORT)

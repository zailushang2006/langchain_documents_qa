#!/usr/bin/env python3
# -*- coding: utf-8 -*-
' a test aiohttp Websocket Client '

__author__ = 'TianJiang Gui'

import aiohttp
from aiohttp import web
import asyncio

import json


async def callback(msg):
    print('callback:', msg)


async def websocket(session, url):
    params = {'name': '桂天江', 'age': '33'}
    params = {
        # "query": "How many people are serving in the Iranian military",
        "query": "How to use PromptTemplate",
        "chat_history": [],
        "category": "strategy",
        "stream": "true"
    }

    async with session.ws_connect(url) as ws:
        # ---gtj 一定注意中文发送前要采用ensure_ascii=False
        jsondata = json.dumps(params, ensure_ascii=False)
        print('send jsondata:', type(jsondata), jsondata, type(params), params)
        await ws.send_json(jsondata)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await callback(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print("aiohttp.WSMsgType.CLOSED: ", msg)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("aiohttp.WSMsgType.ERROR: ", msg)
                break
        await ws.close()


async def main(app):
    session = aiohttp.ClientSession()
    # await websocket(session, 'http://127.0.0.1:8900/ws')
    await websocket(session, 'http://127.0.0.1:9000/chat')


if __name__ == '__main__':
    app = web.Application()
    asyncio.run(main(app))
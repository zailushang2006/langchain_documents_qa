#!/usr/bin/env python3
# -*- coding: utf-8 -*-
' a test aiohttp Websocket Server '

__author__ = 'TianJiang Gui'

import aiohttp
from aiohttp import web
import json


async def hello(request):
    return web.Response(text="Hello, world")


async def websocket_handler(request):
    # ws对象
    ws = web.WebSocketResponse()
    # 等待用户连接
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                # ---gtj 注意如果带中文的显示内容
                print('msg.data:', type(msg.data), msg.data)
                jddd = json.loads(msg.data)
                # ---gtj 如果带中文就显示正确了
                print('jddd', type(jddd), jddd)
                # ---gtj str转换dict
                dicts = eval(jddd)
                # ---gtj 从json中获取数据
                name = dicts['name']
                age = dicts['age']
                await ws.send_str('[%s]:%s 你好' % (name, age))
                print('dicts:', type(dicts), dicts)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    # 断开连接了
    print('websocket connection closed')
    return ws


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/', hello)])
    app.add_routes([web.get('/ws', websocket_handler)])

    web.run_app(app, host='127.0.0.1', port=8900)
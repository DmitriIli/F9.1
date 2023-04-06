import os
from aiohttp import web
import json

news_dict = [
    {'id': 1, 'title': 'title1', 'text': 'text1'},
    {'id': 2, 'title': 'title2', 'text': 'text2'},
    {'id': 3, 'title': 'title3', 'text': 'text3'}
]

news_json = json.dumps(news_dict)

WS_FILE = os.path.join(os.path.dirname(__file__),'index.html')

async def handler(request: web.Request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str(news_json)

    try:
        print("Someone joined.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone joined")
        request.app["sockets"].append(resp)

        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone disconnected.")

   
async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close() 


def init():
    app = web.Application()
    app["sockets"] = []
    app.add_routes([web.get("/ws", handler)])
    app.on_shutdown.append(on_shutdown) 
    return app


web.run_app(init())

import asyncio
import json
import time
from time import strftime, localtime
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


html = """
<!DOCTYPE html>
<html>
  <head>
    <title>WebSocket Time Test</title>
  </head>
  <body>
    <h1>Current Time (from Pi)</h1>
    <div id="clock">Connecting...</div>

    <script src="/static/app.js"></script>
  </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            await ws.send_text(current_time)
            await asyncio.sleep(1)
    except Exception:
        pass  # client disconnected
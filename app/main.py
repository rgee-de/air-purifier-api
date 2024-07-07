import asyncio
import logging
import threading
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from app.config import HOST_IP, LOG_LEVEL
from app.routes import control, status
from app.services.status_observe import StatusObserver
from app.utils.globals import websocket_manager, latest_status

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    status_observe = StatusObserver(HOST_IP, update_status)
    thread = threading.Thread(target=status_observe.run)
    thread.daemon = True
    thread.start()

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(control.router)
app.include_router(status.router)


def update_status(purifier_status: dict):
    latest_status.update(purifier_status)
    logger.info("Received status: %s", purifier_status)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_manager.broadcast(latest_status))
    loop.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)


@app.get("/")
def get_websocket_example():
    file_path = os.path.join(os.path.dirname(__file__), "templates", "websocket_example.html")
    with open(file_path, "r") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

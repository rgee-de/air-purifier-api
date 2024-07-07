import asyncio
import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.config import HOST_IP, LOG_LEVEL, ORIGINS, WEBSOCKET_URL
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")


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
def get_websocket_example(request: Request):
    return templates.TemplateResponse("websocket_example.html", {"request": request, "websocket_url": WEBSOCKET_URL})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

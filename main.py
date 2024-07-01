import json
import logging
import os
import subprocess
import threading

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.status import StatusModel
from status_observe import run_subprocess


load_dotenv()
app = FastAPI()

air_purifier_host = os.getenv("HOST_IP")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Zwischenspeicher für den letzten JSON-Zustand
latest_status = StatusModel().dict()


def update_status(status: str):
    logger.info("Received status: %s", status)
    global latest_status
    if not status:
        latest_status = StatusModel().dict()  # Reset to default values if no data
    else:
        try:
            json_string = status.replace("'", '"')
            json_string = json_string.replace('False', 'false').replace('True', 'true').replace('None', 'null')
            status_dict = json.loads(json_string)
            latest_status.update(status_dict)  # Update with the received data
        except json.JSONDecodeError:
            logger.error("Failed to decode status string: %s", status)


def run_aioairctrl_set(sets):
    command = ['aioairctrl', '--host', air_purifier_host, 'set'] + sets
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e), "output": e.output}


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=run_subprocess, args=(air_purifier_host, update_status))
    thread.daemon = True
    thread.start()


origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def get_status():
    return latest_status


@app.post("/mode_p")
def mode_p():
    run_aioairctrl_set(['mode=P', 'uil=0', 'aqil=0'])
    return {}


@app.post("/mode_a")
def mode_a():
    run_aioairctrl_set(['mode=A', 'uil=0', 'aqil=0'])
    return {}


@app.post("/turbo")
def turbo():
    run_aioairctrl_set(['om=t', 'uil=0', 'aqil=0'])
    return {}


@app.post("/sleep")
def sleep():
    run_aioairctrl_set(['om=s', 'uil=0', 'aqil=0'])
    return {}


@app.post("/stop")
def stop():
    run_aioairctrl_set(['pwr=0'])
    return {}


@app.post("/start")
def start():
    run_aioairctrl_set(['pwr=1'])
    return {}


if __name__ == "__main__":
    # Starten der FastAPI-Anwendung
    uvicorn.run(app, host="0.0.0.0", port=8000)

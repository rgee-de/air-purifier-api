from fastapi import FastAPI
import threading
import logging
from status_observe import run_subprocess
import uvicorn
import subprocess

app = FastAPI()
host = "192.168.20.45"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Zwischenspeicher für den letzten JSON-Zustand
latest_status = {}

def update_status(status):
    logger.info("Received status: %s", status)
    global latest_status
    latest_status = status

@app.get("/status")
def get_status():
    return latest_status

@app.on_event("startup")
def on_startup():
    # Starten des Subprozesses in einem separaten Thread
    host = "192.168.20.45"
    thread = threading.Thread(target=run_subprocess, args=(host, update_status))
    thread.daemon = True
    thread.start()

@app.get("/mode_p")
async def mode_p():
    subprocess.run(['aioairctrl', '--host', host, 'set', 'mode=P', 'uil=0', 'aqil=0'])
    return {}

@app.get("/mode_a")
async def mode_p():
    subprocess.run(['aioairctrl', '--host', host, 'set', 'mode=A', 'uil=0', 'aqil=0'])
    return {}

@app.get("/turbo")
async def mode_p():
    subprocess.run(['aioairctrl', '--host', host, 'set', 'om=t', 'uil=0', 'aqil=0'])
    return {}

@app.get("/sleep")
async def mode_p():
    subprocess.run(['aioairctrl', '--host', host, 'set', 'om=s', 'uil=0', 'aqil=0'])
    return {}

@app.get("/stop")
async def mode_p():
    subprocess.run(['aioairctrl', '--host', host, 'set', 'pwr=0'])
    return {}

@app.get("/start")
async def mode_p():
    subprocess.run(['aioairctrl', '--host', host, 'set', 'pwr=1'])
    return {}


if __name__ == "__main__":
    # Starten der FastAPI-Anwendung
    uvicorn.run(app, host="0.0.0.0", port=8000)

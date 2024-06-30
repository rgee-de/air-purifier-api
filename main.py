from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import subprocess
import asyncio
import re
from enum import Enum
from typing import Dict

app = FastAPI()

IPADDR = "192.168.20.45"
PROTOCOL = "coap"
RETRY_DELAY = 1  # delay between retries in seconds
MAX_RETRIES = 3  # maximum number of retries

class AirCommand(str, Enum):
    Start = "Start"
    Stop = "Stop"
    Sleep = "Sleep"
    Allergy = "Allergy"
    Turbo = "Turbo"
    Info = "Info"

class AirStatus(BaseModel):
    name: str
    type: str
    modelid: str
    swversion: str
    range: str
    runtime: str
    rssi: str
    otacheck: str
    wifilog: str
    free_memory: str
    wifiVersion: str
    productId: str
    deviceId: str
    statusType: str
    connectType: str
    om: str
    pwr: str
    cl: str
    aqil: str  # Light brightness
    uil: str  # Buttons light
    mode: str
    pm25: str
    iaql: str  # Allergen index
    aqit: str  # Air quality notification threshold
    aqit_ext: str
    ddp: str  # Used index
    fltt1: str  # HEPA filter type
    fltt2: str  # Active carbon filter type
    fltsts0: str  # Pre-filter and Wick
    fltsts1: str  # HEPA filter
    fltsts2: str  # Active carbon filter

class CommandResponse(BaseModel):
    status: str

async def execute_terminal(command, args, check_stdout_fn=lambda x: True, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    attempt = 0

    async def execute():
        process = await asyncio.create_subprocess_exec(
            command, *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()

    while attempt < max_retries:
        code, stdout, stderr = await execute()
        if code == 0 and check_stdout_fn(stdout):
            return stdout
        attempt += 1
        if attempt < max_retries:
            await asyncio.sleep(retry_delay)
        else:
            raise Exception(f"Failed after {max_retries} retries. Error: {stderr}")

def airctrl_status_output_to_json(output: str) -> AirStatus:
    pattern = re.compile(r"\[([^\]]+)] ([^\[]+)")
    matches = pattern.findall(output)
    json_data: Dict[str, str] = {match[0].strip().lower(): match[1].strip() for match in matches}
    return AirStatus(**json_data)

@app.get("/handler", response_model=CommandResponse)
async def handler(command: AirCommand):
    if command == AirCommand.Stop:
        return await stop()
    elif command == AirCommand.Sleep:
        return await sleep()
    elif command == AirCommand.Turbo:
        return await turbo()
    elif command == AirCommand.Allergy:
        return await allergy()
    elif command == AirCommand.Info:
        return await info()
    else:
        raise HTTPException(status_code=400, detail="Invalid command")

async def start():
    command = "airctrl"
    args = [f"--ipaddr={IPADDR}", f"--protocol={PROTOCOL}", "--pwr=1", "--aqil=0", "--uil=0", "--debug"]
    try:
        await execute_terminal(command, args, lambda d: "failed" not in d)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stop() -> CommandResponse:
    command = "airctrl"
    args = [f"--ipaddr={IPADDR}", f"--protocol={PROTOCOL}", "--pwr=0", "--debug"]
    try:
        await execute_terminal(command, args, lambda d: "failed" not in d)
        return CommandResponse(status="stopped")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def sleep() -> CommandResponse:
    command = "airctrl"
    args = [f"--ipaddr={IPADDR}", f"--protocol={PROTOCOL}", "--om=s", "--aqil=0", "--uil=0", "--debug"]
    try:
        await execute_terminal(command, args, lambda d: "failed" not in d)
        return CommandResponse(status="sleep mode activated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def turbo() -> CommandResponse:
    command = "airctrl"
    args = [f"--ipaddr={IPADDR}", f"--protocol={PROTOCOL}", "--om=t", "--aqil=100", "--uil=1", "--debug"]
    try:
        await execute_terminal(command, args, lambda d: "failed" not in d)
        return CommandResponse(status="turbo mode activated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def allergy() -> CommandResponse:
    command = "airctrl"
    args = [f"--ipaddr={IPADDR}", f"--protocol={PROTOCOL}", "--mode=P", "--aqil=0", "--uil=0", "--debug"]
    try:
        await execute_terminal(command, args, lambda d: "failed" not in d)
        return CommandResponse(status="allergy mode activated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info", response_model=AirStatus)
async def info() -> AirStatus:
    command = "airctrl"
    args = [f"--ipaddr={IPADDR}", f"--protocol={PROTOCOL}"]
    try:
        output = await execute_terminal(command, args, lambda d: "Unexpected error:" not in d)
        data = airctrl_status_output_to_json(output)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

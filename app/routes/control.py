import subprocess

from fastapi import APIRouter

from app.config import HOST_IP

router = APIRouter()

UIL_OFF = "uil=0"
AQIL_OFF = "aqil=0"
COMMON_ARGS = [UIL_OFF, AQIL_OFF]

def run_aioairctrl_set(sets):
    command = ['aioairctrl', '--host', HOST_IP, 'set'] + sets
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e), "output": e.output}


@router.post("/mode_p")
def mode_p():
    run_aioairctrl_set(['mode=P', *COMMON_ARGS])
    return {}


@router.post("/mode_a")
def mode_a():
    run_aioairctrl_set(['mode=A', *COMMON_ARGS])
    return {}


@router.post("/turbo")
def turbo():
    run_aioairctrl_set(['om=t', *COMMON_ARGS])
    return {}


@router.post("/sleep")
def sleep():
    run_aioairctrl_set(['om=s', *COMMON_ARGS])
    return {}


@router.post("/stop")
def stop():
    run_aioairctrl_set(['pwr=0'])
    return {}


@router.post("/start")
def start():
    run_aioairctrl_set(['pwr=1'])
    return {}

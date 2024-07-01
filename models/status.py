from pydantic import BaseModel


class StatusModel(BaseModel):
    name: str = ''
    type: str = ''
    modelid: str = ''
    swversion: str = ''
    range: str = ''
    Runtime: int = 0
    rssi: int = 0
    otacheck: bool = False
    wifilog: bool = False
    free_memory: int = 0
    WifiVersion: str = ''
    ProductId: str = ''
    DeviceId: str = ''
    StatusType: str = ''
    ConnectType: str = ''
    om: str = ''
    pwr: str = ''
    cl: bool = False
    aqil: int = 0
    uil: str = ''
    dt: int = 0
    dtrs: int = 0
    mode: str = ''
    pm25: int = 0
    iaql: int = 0
    aqit: int = 0
    aqit_ext: int = 0
    ddp: str = ''
    err: int = 0
    fltt1: str = ''
    fltt2: str = ''
    fltsts0: int = 0
    fltsts1: int = 0
    fltsts2: int = 0

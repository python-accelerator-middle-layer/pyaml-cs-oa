from pydantic import BaseModel


class EpicsConfigR(BaseModel):
    read_pvname: str
    timeout_ms: int = 3000

class EpicsConfigW(BaseModel):
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None

class EpicsConfigRW(BaseModel):
    read_pvname: str
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None


class TangoConfigR(BaseModel):
    attribute: str
    timeout_ms: int = 3000

class TangoConfigRW(BaseModel):
    attribute: str
    timeout_ms: int = 3000
    range: list[float] | None = None


ControlSysConfig = (
    EpicsConfigR
    | EpicsConfigW
    | EpicsConfigRW
    | TangoConfigR
    | TangoConfigRW
)

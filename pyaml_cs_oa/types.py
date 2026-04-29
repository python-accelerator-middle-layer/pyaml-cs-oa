from pydantic import BaseModel, ConfigDict


class EpicsConfigR(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read_pvname: str
    timeout_ms: int = 3000
    index: int | None = None

class EpicsConfigW(BaseModel):
    model_config = ConfigDict(extra="forbid")
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None

class EpicsConfigRW(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read_pvname: str
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None

class TangoConfigR(BaseModel):
    attribute: str
    timeout_ms: int = 3000
    index: int | None = None

class TangoConfigRW(BaseModel):
    attribute: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None


ControlSysConfig = (
    EpicsConfigR
    | EpicsConfigW
    | EpicsConfigRW
    | TangoConfigR
    | TangoConfigRW
)

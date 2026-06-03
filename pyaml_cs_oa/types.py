from pydantic import BaseModel, ConfigDict


class EpicsConfigR(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read_pvname: str
    timeout_ms: int = 3000
    index: int | None = None
    unit: str = ""


class EpicsConfigW(BaseModel):
    model_config = ConfigDict(extra="forbid")
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None
    unit: str = ""


class EpicsConfigRW(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read_pvname: str
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None
    unit: str = ""


class TangoConfigAtt(BaseModel):
    attribute: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None
    unit: str = ""


ControlSysConfig = EpicsConfigR | EpicsConfigW | EpicsConfigRW | TangoConfigAtt

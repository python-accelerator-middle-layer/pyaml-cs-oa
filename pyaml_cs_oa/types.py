from pydantic import BaseModel


class EpicsConfigR(BaseModel):
    read_pvname: str


class EpicsConfigW(BaseModel):
    write_pvname: str


class EpicsConfigRW(EpicsConfigR, EpicsConfigW):
    pass


class TangoConfigR(BaseModel):
    attribute: str


class TangoConfigRW(BaseModel):
    attribute: str


ControlSysConfig = (
    EpicsConfigR
    | EpicsConfigW
    | EpicsConfigRW
    | TangoConfigR
    | TangoConfigRW
)

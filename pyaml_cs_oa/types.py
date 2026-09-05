"""Pydantic configuration models for supported control systems."""

from pydantic import BaseModel, ConfigDict


class EpicsConfigR(BaseModel):
    """Configuration for a read-only EPICS process variable."""

    model_config = ConfigDict(extra="forbid")
    read_pvname: str
    timeout_ms: int = 3000
    index: int | None = None
    unit: str = ""


class EpicsConfigW(BaseModel):
    """Configuration for a write-only EPICS process variable."""

    model_config = ConfigDict(extra="forbid")
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None
    unit: str = ""


class EpicsConfigRW(BaseModel):
    """Configuration for a readable and writable EPICS process variable pair."""

    model_config = ConfigDict(extra="forbid")
    read_pvname: str
    write_pvname: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None
    unit: str = ""


class TangoConfigAtt(BaseModel):
    """Configuration for a Tango attribute."""

    attribute: str
    timeout_ms: int = 3000
    range: list[float] | None = None
    index: int | None = None
    unit: str = ""


ControlSysConfig = EpicsConfigR | EpicsConfigW | EpicsConfigRW | TangoConfigAtt

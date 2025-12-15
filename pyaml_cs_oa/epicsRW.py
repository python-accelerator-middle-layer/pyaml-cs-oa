from .core import FloatSignalContainer
from .types import EpicsConfigRW

PYAMLCLASS : str = "EpicsRW"

class ConfigModel(EpicsConfigRW):
    unit: str = ""

class EpicsRW(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
    def get_cs(self) -> str:
        return "epics"        
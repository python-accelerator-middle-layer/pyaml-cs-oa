from .core import FloatSignalContainer
from .types import EpicsConfigW

PYAMLCLASS : str = "EpicsW"

class ConfigModel(EpicsConfigW):
    unit: str = ""

class EpicsW(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
    def get_cs(self) -> str:
        return "epics"        
from .float_signal import FloatSignalContainer
from .types import EpicsConfigR

PYAMLCLASS: str = "EpicsR"


class ConfigModel(EpicsConfigR): ...


class EpicsR(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def get_cs(self) -> str:
        return "epics"

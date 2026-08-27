from .float_signal import FloatSignalContainer
from .types import EpicsConfigR

PYAMLCLASS: str = "EpicsR"


class EpicsR(FloatSignalContainer):
    def __init__(self, cfg: EpicsConfigR):
        super().__init__(cfg)

    def get_cs(self) -> str:
        return "epics"

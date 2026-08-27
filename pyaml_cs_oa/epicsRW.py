from .float_signal import FloatSignalContainer
from .types import EpicsConfigRW

PYAMLCLASS: str = "EpicsRW"


class EpicsRW(FloatSignalContainer):
    def __init__(self, cfg: EpicsConfigRW):
        super().__init__(cfg)

    def get_cs(self) -> str:
        return "epics"

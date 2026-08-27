from .float_signal import FloatSignalContainer
from .types import EpicsConfigW

PYAMLCLASS: str = "EpicsW"


class EpicsW(FloatSignalContainer):
    def __init__(self, cfg: EpicsConfigW):
        super().__init__(cfg)

    def get_cs(self) -> str:
        return "epics"

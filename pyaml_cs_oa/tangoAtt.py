from .float_signal import FloatSignalContainer
from .types import TangoConfigAtt

PYAMLCLASS: str = "TangoRW"


class TangoAtt(FloatSignalContainer):
    def __init__(self, cfg: TangoConfigAtt):
        super().__init__(cfg)

    def get_cs(self) -> str:
        return "tango"

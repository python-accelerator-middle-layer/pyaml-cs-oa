from .float_signal import FloatSignalContainer
from .types import TangoConfigRW

PYAMLCLASS : str = "TangoRW"

class ConfigModel(TangoConfigRW):
    unit: str = ""

class TangoRW(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
    def get_cs(self) -> str:
        return "tango"
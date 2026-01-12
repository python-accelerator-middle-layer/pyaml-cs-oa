from .float_signal import FloatSignalContainer
from .types import TangoConfigR

PYAMLCLASS : str = "TangoR"

class ConfigModel(TangoConfigR):
    unit: str = ""

class TangoR(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
    def get_cs(self) -> str:
        return "tango"        
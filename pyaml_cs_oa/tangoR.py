from .float_signal import FloatSignalContainer
from .types import TangoConfigR

PYAMLCLASS : str = "TangoR"

class ConfigModel(TangoConfigR):
    unit: str = ""

class TangoR(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel, is_array=False):
        super().__init__(cfg,is_array)
    def get_cs(self) -> str:
        return "tango"        
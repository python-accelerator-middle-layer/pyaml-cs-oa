from .float_signal import FloatSignalContainer
from .types import EpicsConfigR

PYAMLCLASS : str = "EpicsR"

class ConfigModel(EpicsConfigR):
    unit: str = ""

class EpicsR(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel, is_array=False):
        super().__init__(cfg,is_array)
    def get_cs(self) -> str:
        return "epics"        
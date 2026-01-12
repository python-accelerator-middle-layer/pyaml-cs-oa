from .float_signal import FloatSignalContainer
from .types import EpicsConfigW

PYAMLCLASS : str = "EpicsW"

class ConfigModel(EpicsConfigW):
    unit: str = ""

class EpicsW(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel, is_array=False):
        super().__init__(cfg,is_array)
    def get_cs(self) -> str:
        return "epics"        
from .float_signal import FloatSignalContainer
from .types import EpicsConfigRW

PYAMLCLASS: str = "EpicsRW"


class ConfigModel(EpicsConfigRW): ...


class EpicsRW(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel, is_array: bool = False):
        super().__init__(cfg, is_array)

    def get_cs(self) -> str:
        return "epics"

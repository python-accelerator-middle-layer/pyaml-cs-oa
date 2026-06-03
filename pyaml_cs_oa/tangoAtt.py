from .float_signal import FloatSignalContainer
from .types import TangoConfigAtt

PYAMLCLASS: str = "TangoRW"


class ConfigModel(TangoConfigAtt): ...


class TangoAtt(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel, is_array: bool = False):
        super().__init__(cfg, is_array)

    def get_cs(self) -> str:
        return "tango"

from .float_signal import FloatSignalContainer
from .types import TangoConfigAtt

PYAMLCLASS: str = "TangoRW"


class ConfigModel(TangoConfigAtt): ...


class TangoAtt(FloatSignalContainer):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def get_cs(self) -> str:
        return "tango"

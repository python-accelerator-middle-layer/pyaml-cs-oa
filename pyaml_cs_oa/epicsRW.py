"""Read/write EPICS signal implementation."""

from .float_signal import FloatSignalContainer
from .types import EpicsConfigRW

PYAMLCLASS: str = "EpicsRW"


class ConfigModel(EpicsConfigRW):
    """Configuration model registered for the ``EpicsRW`` device class."""


class EpicsRW(FloatSignalContainer):
    """PyAML read/write signal backed by an EPICS signal."""

    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "epics"

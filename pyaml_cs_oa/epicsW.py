"""Write-only EPICS signal implementation."""

from .float_signal import FloatSignalContainer
from .types import EpicsConfigW

PYAMLCLASS: str = "EpicsW"


class ConfigModel(EpicsConfigW):
    """Configuration model registered for the ``EpicsW`` device class."""


class EpicsW(FloatSignalContainer):
    """PyAML write-only signal backed by an EPICS write signal."""

    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "epics"

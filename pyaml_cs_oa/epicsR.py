"""Read-only EPICS signal implementation."""

from .float_signal import FloatSignalContainer
from .types import EpicsConfigR

PYAMLCLASS: str = "EpicsR"


class ConfigModel(EpicsConfigR):
    """Configuration model registered for the ``EpicsR`` device class."""


class EpicsR(FloatSignalContainer):
    """PyAML read-only signal backed by an EPICS read signal."""

    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "epics"

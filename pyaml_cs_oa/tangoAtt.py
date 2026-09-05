"""Tango attribute signal implementation."""

from .float_signal import FloatSignalContainer
from .types import TangoConfigAtt

PYAMLCLASS: str = "TangoRW"


class ConfigModel(TangoConfigAtt):
    """Configuration model registered for the ``TangoAtt`` device class."""


class TangoAtt(FloatSignalContainer):
    """PyAML signal backed by a Tango attribute."""

    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "tango"

"""Read-only EPICS signal implementation."""

from pyaml.validation import DynamicValidation, register_schema

from .float_signal import FloatSignalContainer
from .types import EpicsConfigR

PYAMLCLASS: str = "EpicsR"


@register_schema
class EpicsR(FloatSignalContainer, DynamicValidation):
    """PyAML read-only signal backed by an EPICS read signal."""

    def __init__(self, read_pvname: str, timeout_ms: int = 3000, index: int | None = None, unit: str = ""):
        cfg = EpicsConfigR(read_pvname=read_pvname, timeout_ms=timeout_ms, index=index, unit=unit)
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "epics"

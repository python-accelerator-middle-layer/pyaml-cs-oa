"""Tango attribute signal implementation."""

from pyaml.validation import DynamicValidation, register_schema

from .float_signal import FloatSignalContainer
from .types import TangoConfigAtt

PYAMLCLASS: str = "TangoRW"


@register_schema
class TangoAtt(FloatSignalContainer, DynamicValidation):
    """PyAML signal backed by a Tango attribute."""

    def __init__(
        self,
        attribute: str,
        timeout_ms: int = 3000,
        range: list[float] | None = None,
        index: int | None = None,
        unit: str = "",
    ):
        cfg = TangoConfigAtt(attribute=attribute, timeout_ms=timeout_ms, range=range, index=index, unit=unit)
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "tango"

"""Write-only EPICS signal implementation."""

from pyaml.validation import DynamicValidation, register_schema

from .float_signal import FloatSignalContainer
from .types import EpicsConfigW

PYAMLCLASS: str = "EpicsW"


@register_schema
class EpicsW(FloatSignalContainer, DynamicValidation):
    """PyAML write-only signal backed by an EPICS write signal."""

    def __init__(
        self,
        write_pvname: str,
        timeout_ms: int = 3000,
        range: list[float] | None = None,
        index: int | None = None,
        unit: str = "",
    ):
        cfg = EpicsConfigW(
            write_pvname=write_pvname,
            timeout_ms=timeout_ms,
            range=range,
            index=index,
            unit=unit,
        )
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "epics"

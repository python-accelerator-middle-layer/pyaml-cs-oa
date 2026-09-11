"""Read/write EPICS signal implementation."""

from pyaml.validation import DynamicValidation, register_schema

from .float_signal import FloatSignalContainer
from .types import EpicsConfigRW

PYAMLCLASS: str = "EpicsRW"


@register_schema
class EpicsRW(FloatSignalContainer, DynamicValidation):
    """PyAML read/write signal backed by an EPICS signal."""

    def __init__(
        self,
        read_pvname: str,
        write_pvname: str,
        timeout_ms: int = 3000,
        range: list[float] | None = None,
        index: int | None = None,
        unit: str = "",
    ):
        cfg = EpicsConfigRW(
            read_pvname=read_pvname, write_pvname=write_pvname, timeout_ms=timeout_ms, range=range, index=index, unit=unit
        )
        super().__init__(cfg)

    def get_cs(self) -> str:
        """Return the control-system identifier."""
        return "epics"

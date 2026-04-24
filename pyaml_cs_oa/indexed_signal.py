from pyaml.common.exception import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess

from .container import OAReadback, OASetpoint


class IndexedFloatSignal(DeviceAccess):
    """DeviceAccess that combines independently-built read and write signals.

    Used when at least one side is an indexed array element, or when the
    read and write PVs must be built as separate signals (mixed scalar/array).
    """

    def __init__(
        self,
        rb: OAReadback | None,
        sp: OASetpoint | None,
        unit: str = "",
        range: list | None = None,
        measure_name: str = "",
    ):
        self._rb = rb
        self._sp = sp
        self._unit = unit
        self._range = range or [None, None]
        self._measure_name = measure_name
        self._writable = sp is not None
        self._readable = rb is not None

    def get(self):
        if self._writable:
            return self._sp.get()
        return self._rb.get()

    def readback(self):
        return self._rb.get()

    def set(self, value):
        if not self._writable:
            raise PyAMLException("IndexedFloatSignal is read-only: individual element writes are not supported.")
        return self._sp.set(value)

    def set_and_wait(self, value):
        if not self._writable:
            raise PyAMLException("IndexedFloatSignal is read-only: individual element writes are not supported.")
        return self._sp.set(value)

    def unit(self) -> str:
        return self._unit

    def get_range(self) -> list:
        return self._range

    def measure_name(self) -> str:
        return self._measure_name

    def name(self) -> str:
        return self._measure_name

    def check_device_availability(self) -> bool:
        return True

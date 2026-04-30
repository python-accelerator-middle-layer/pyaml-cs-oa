import numpy as np
import pytest
from pyaml import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess

from pyaml_cs_oa.float_signal import FloatSignalContainer
from pyaml_cs_oa.scalar_aggregator import OAScalarAggregator
from pyaml_cs_oa.types import EpicsConfigR


class FakeScalarSignal(FloatSignalContainer):
    """FloatSignalContainer test double with fake SP/RB sides."""

    def __init__(self, value: float, writable: bool = True) -> None:
        super().__init__(EpicsConfigR(read_pvname="PV:RB"), is_array=False)
        self._writable = writable
        self.SP = _FakeSide(value, signal_key=object())
        self.RB = _FakeSide(value, signal_key=object())

    def get_range(self) -> list[float | None]:
        return [None, None]


class _FakeSide:
    def __init__(self, value: float, signal_key: object) -> None:
        self.value = value
        self._r_sig = signal_key
        self._w_sig = signal_key
        self.completed_values: list[float] = []

    async def async_get(self) -> float:
        return self.value

    async def _complete_set(self, value: float):
        self.completed_values.append(value)
        self.value = value
        return None


class WrongDevice(DeviceAccess):
    def get(self):
        return None

    def readback(self):
        return None

    def set(self, value):
        return None

    def set_and_wait(self, value):
        return None

    def unit(self) -> str:
        return ""

    def get_range(self) -> list:
        return [None, None]

    def measure_name(self) -> str:
        return "wrong"

    def name(self) -> str:
        return "wrong"

    def check_device_availability(self) -> bool:
        return True


def test_add_devices_rejects_single_wrong_device() -> None:
    aggregator = OAScalarAggregator()

    with pytest.raises(PyAMLException, match="All devices must be instances"):
        aggregator.add_devices(WrongDevice())


def test_add_devices_rejects_wrong_device_in_list() -> None:
    aggregator = OAScalarAggregator()

    with pytest.raises(PyAMLException, match="All devices must be instances"):
        aggregator.add_devices([FakeScalarSignal(1.0), WrongDevice()])


def test_get_returns_values_in_device_order() -> None:
    aggregator = OAScalarAggregator()
    aggregator.add_devices([FakeScalarSignal(1.0), FakeScalarSignal(2.0)])

    np.testing.assert_array_equal(aggregator.get(), np.array([1.0, 2.0]))


def test_set_writes_values_in_device_order() -> None:
    first = FakeScalarSignal(1.0)
    second = FakeScalarSignal(2.0)
    aggregator = OAScalarAggregator()
    aggregator.add_devices([first, second])

    aggregator.set(np.array([10.0, 20.0]))

    assert first.SP.completed_values == [10.0]
    assert second.SP.completed_values == [20.0]


def test_set_rejects_length_mismatch() -> None:
    aggregator = OAScalarAggregator()
    aggregator.add_devices([FakeScalarSignal(1.0), FakeScalarSignal(2.0)])

    with pytest.raises(PyAMLException, match="do not match"):
        aggregator.set(np.array([10.0]))


def test_readback_returns_readback_values_in_device_order() -> None:
    aggregator = OAScalarAggregator()
    aggregator.add_devices([FakeScalarSignal(3.0), FakeScalarSignal(4.0)])

    np.testing.assert_array_equal(aggregator.readback(), np.array([3.0, 4.0]))

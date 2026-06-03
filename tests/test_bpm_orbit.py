from typing import Any
from pydantic import BaseModel, ConfigDict

import numpy as np
from pyaml.arrays.bpm_array import BPMArray
from pyaml.bpm.bpm import BPM
from pyaml.bpm.bpm import ConfigModel as BPMConfig
from pyaml.bpm.bpm_simple_model import BPMSimpleModel
from pyaml.bpm.bpm_simple_model import ConfigModel as BPMSimpleModelConfig
from pyaml.control.abstract_impl import RBpmArray
from pyaml.control.deviceaccess import DeviceAccess

from pyaml_cs_oa.catalog import Catalog
from pyaml_cs_oa.controlsystem import ConfigModel, OphydAsyncControlSystem
from pyaml_cs_oa.float_signal import FloatSignalContainer
from pyaml_cs_oa.types import EpicsConfigR


class VectorDevice(DeviceAccess):
    """DeviceAccess fake returning one shared BPM orbit vector."""

    def __init__(self, name: str, value: list[float]) -> None:
        self._name = name
        self._value = np.array(value, dtype=float)
        self.get_calls = 0

    def get(self) -> np.ndarray:
        self.get_calls += 1
        return self._value.copy()

    def readback(self) -> np.ndarray:
        return self.get()

    def set(self, value: Any) -> None:
        self._value = np.array(value, dtype=float)

    def set_and_wait(self, value: Any) -> None:
        self.set(value)

    def unit(self) -> str:
        return "m"

    def get_range(self) -> list[float | None]:
        return [None, None]

    def measure_name(self) -> str:
        return self._name

    def name(self) -> str:
        return self._name

    def check_device_availability(self) -> bool:
        return True


class _VectorReadSide:
    def __init__(self, source: VectorDevice) -> None:
        self._r_sig = source
        self._source = source

    async def async_get(self) -> np.ndarray:
        return self._source.get()

    def get(self) -> np.ndarray:
        return self._source.get()

class IndexedVectorSignalConfig(EpicsConfigR):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    source : VectorDevice

class IndexedVectorSignal(FloatSignalContainer):
    """FloatSignalContainer fake resolving one indexed value from a shared vector."""

    def __init__(self, config: IndexedVectorSignalConfig) -> None:
        super().__init__(config, is_array=True)
        self._readable = True
        self._writable = False
        self.RB = _VectorReadSide(config.source)
        self.SP = None

    def name(self) -> str:
        return f"{self._cfg.read_pvname}[{self._cfg.index}]"


class StaticCatalog(Catalog):
    def __init__(self, devices: dict[str, DeviceAccess]) -> None:
        self._devices = devices

    def resolve(self, key: str) -> BaseModel:
        return self._devices[key]


class IdentityAttachControlSystem(OphydAsyncControlSystem):
    """Control system fake that keeps pre-built DeviceAccess objects attached."""

    # attach public methods are depecrated

    def get_device(self, ref: str | BaseModel | None) -> DeviceAccess | None:
       config =  self._cfg.catalog.resolve(ref)
       return IndexedVectorSignal(config)

def _attached_indexed_bpm(
    control_system: IdentityAttachControlSystem,
    bpm_index: int,
) -> BPM:
    model = BPMSimpleModel(
        BPMSimpleModelConfig(
            x_pos=f"BPM{bpm_index}:X",
            y_pos=f"BPM{bpm_index}:Y",
        ),
    )
    x_pos, y_pos = control_system.get_devices(model.get_pos_devices())
    bpm = BPM(BPMConfig(name=f"BPM{bpm_index}", model=model))

    return bpm.attach(
        control_system,
        RBpmArray(x_pos, y_pos),
        offset=None,
        tilt=None,
    )


def _control_system_with_indexed_orbit(orbit_device: VectorDevice, bpm_count: int) -> IdentityAttachControlSystem:
    catalog = StaticCatalog(
        {f"BPM{bpm_index}:X": IndexedVectorSignalConfig(source=orbit_device, 
                                                        read_pvname=orbit_device.name(), 
                                                        unit=orbit_device.unit(), 
                                                        index=2 * bpm_index) for bpm_index in range(bpm_count)}
      | {f"BPM{bpm_index}:Y": IndexedVectorSignalConfig(source=orbit_device, 
                                                        read_pvname=orbit_device.name(), 
                                                        unit=orbit_device.unit(), 
                                                        index=2 * bpm_index + 1) for bpm_index in range(bpm_count)},
    )
    control_system = IdentityAttachControlSystem(ConfigModel(name="live",catalog=catalog))
    return control_system


def test_indexed_bpm_orbit_aggregator_keeps_distinct_positions() -> None:
    """Regression test for BPM orbit reads backed by one indexed vector PV."""

    orbit_device = VectorDevice("BPM:ORBIT", [3285.83564, 0.0, 2195.12518, 0.0])
    control_system = _control_system_with_indexed_orbit(orbit_device, bpm_count=2)
    bpms = [
        _attached_indexed_bpm(control_system, bpm_index=0),
        _attached_indexed_bpm(control_system, bpm_index=1),
    ]

    positions = BPMArray("BPM", bpms, use_aggregator=True).positions

    np.testing.assert_allclose(
        positions.get(),
        np.array(
            [
                [3285.83564, 0.0],
                [2195.12518, 0.0],
            ],
        ),
    )


def test_indexed_bpm_orbit_aggregator_reads_all_bpms_at_once() -> None:
    """A shared vector orbit read should feed every BPM in the array."""

    orbit_device = VectorDevice(
        "BPM:ORBIT",
        [3285.83564, 0.0, 2195.12518, 0.0, 11202.0909, 0.0],
    )
    control_system = _control_system_with_indexed_orbit(orbit_device, bpm_count=3)
    bpms = [
        _attached_indexed_bpm(control_system, bpm_index=0),
        _attached_indexed_bpm(control_system, bpm_index=1),
        _attached_indexed_bpm(control_system, bpm_index=2),
    ]

    positions = BPMArray("BPM", bpms, use_aggregator=True).positions.get()

    assert orbit_device.get_calls == 1
    np.testing.assert_allclose(
        positions,
        np.array(
            [
                [3285.83564, 0.0],
                [2195.12518, 0.0],
                [11202.0909, 0.0],
            ],
        ),
    )


def test_indexed_bpm_orbit_axis_aggregators_keep_distinct_positions() -> None:
    """The horizontal and vertical accessors must keep the same index mapping."""

    orbit_device = VectorDevice(
        "BPM:ORBIT",
        [3285.83564, 0.0, 2195.12518, 0.0, 11202.0909, 0.0],
    )
    control_system = _control_system_with_indexed_orbit(orbit_device, bpm_count=3)
    bpms = [
        _attached_indexed_bpm(control_system, bpm_index=0),
        _attached_indexed_bpm(control_system, bpm_index=1),
        _attached_indexed_bpm(control_system, bpm_index=2),
    ]

    bpm_array = BPMArray("BPM", bpms, use_aggregator=True)

    np.testing.assert_allclose(
        bpm_array.h.get(),
        np.array([3285.83564, 2195.12518, 11202.0909]),
    )
    np.testing.assert_allclose(bpm_array.v.get(), np.zeros(3))

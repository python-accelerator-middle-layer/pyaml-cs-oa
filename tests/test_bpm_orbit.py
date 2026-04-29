from __future__ import annotations

from typing import Any

import numpy as np

from pyaml.arrays.bpm_array import BPMArray
from pyaml.bpm.bpm import BPM, ConfigModel as BPMConfig
from pyaml.bpm.bpm_simple_model import BPMSimpleModel
from pyaml.bpm.bpm_simple_model import ConfigModel as BPMSimpleModelConfig
from pyaml.control.abstract_impl import RBpmArray
from pyaml.control.deviceaccess import DeviceAccess
from pyaml_cs_oa.controlsystem import ConfigModel, OphydAsyncControlSystem


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


class IdentityAttachControlSystem(OphydAsyncControlSystem):
    """Control system fake that keeps pre-built DeviceAccess objects attached."""

    def attach(self, devs: list[DeviceAccess]) -> list[DeviceAccess]:
        return devs

    def attach_array(self, devs: list[DeviceAccess]) -> list[DeviceAccess]:
        return devs


def _attached_indexed_bpm(
    control_system: IdentityAttachControlSystem,
    orbit_device: VectorDevice,
    bpm_index: int,
) -> BPM:
    model = BPMSimpleModel(
        BPMSimpleModelConfig(
            x_pos=orbit_device,
            y_pos=orbit_device,
            x_pos_index=2 * bpm_index,
            y_pos_index=(2 * bpm_index) + 1,
        ),
    )
    bpm = BPM(BPMConfig(name=f"BPM{bpm_index}", model=model))

    return bpm.attach(
        control_system,
        RBpmArray(model, orbit_device, orbit_device),
        offset=None,
        tilt=None,
    )


def test_indexed_bpm_orbit_aggregator_keeps_distinct_positions() -> None:
    """Regression test for BPM orbit reads backed by one indexed vector PV."""

    control_system = IdentityAttachControlSystem(ConfigModel(name="live"))
    orbit_device = VectorDevice("BPM:ORBIT", [3285.83564, 0.0, 2195.12518, 0.0])
    bpms = [
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=0),
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=1),
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

    control_system = IdentityAttachControlSystem(ConfigModel(name="live"))
    orbit_device = VectorDevice(
        "BPM:ORBIT",
        [3285.83564, 0.0, 2195.12518, 0.0, 11202.0909, 0.0],
    )
    bpms = [
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=0),
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=1),
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=2),
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

    control_system = IdentityAttachControlSystem(ConfigModel(name="live"))
    orbit_device = VectorDevice(
        "BPM:ORBIT",
        [3285.83564, 0.0, 2195.12518, 0.0, 11202.0909, 0.0],
    )
    bpms = [
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=0),
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=1),
        _attached_indexed_bpm(control_system, orbit_device, bpm_index=2),
    ]

    bpm_array = BPMArray("BPM", bpms, use_aggregator=True)

    np.testing.assert_allclose(
        bpm_array.h.get(),
        np.array([3285.83564, 2195.12518, 11202.0909]),
    )
    np.testing.assert_allclose(bpm_array.v.get(), np.zeros(3))

"""Aggregators for combining multiple ophyd-async float signals."""

import asyncio

import numpy as np
from numpy import typing as npt
from pyaml import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess
from pyaml.control.deviceaccesslist import DeviceAccessList

from . import arun
from .float_signal import FloatSignalContainer


class OAAggregator(DeviceAccessList):
    """Aggregate scalar or indexed signals into one device-access object."""

    def __init__(self):
        super().__init__()
        self._r_signal_list = {}  # List of signal to read
        self._w_signal_list = {}  # List of signal to read/write
        self._writable = None
        self._items: list[FloatSignalContainer] = []

    def _add_to_dev_list(self, d: FloatSignalContainer):
        # Check type and read/write
        if not isinstance(d, FloatSignalContainer):
            raise PyAMLException("All devices must be instances of FloatSignalContainer.")

        if self._writable is None:
            self._writable = d._writable
        else:
            if self._writable != d._writable:
                raise PyAMLException("Cannot mix read only and read/write signal in a same aggreagator")

        # Construct structure to avoid duplicate reading
        # The shared part is the source Ophyd signal
        if d.RB._r_sig not in self._r_signal_list:
            self._r_signal_list[d.RB._r_sig] = {"source": d.RB, "indices": [[d._cfg.index, len(self._items)]]}
        else:
            self._r_signal_list[d.RB._r_sig]["indices"].append([d._cfg.index, len(self._items)])

        if self._writable:
            if d.SP._w_sig not in self._w_signal_list:
                self._w_signal_list[d.SP._w_sig] = {"source": d.SP, "indices": [[d._cfg.index, len(self._items)]]}
            else:
                self._w_signal_list[d.SP._w_sig]["indices"].append([d._cfg.index, len(self._items)])

        self._items.append(d)

    def add_devices(self, devices: DeviceAccess | list[DeviceAccess]):
        """Add one device or a list of devices to the aggregator.

        Parameters
        ----------
        devices : DeviceAccess or list of DeviceAccess
            Signals to aggregate. All signals must have compatible access modes.
        """
        if isinstance(devices, list):
            for d in devices:
                self._add_to_dev_list(d)
        else:
            self._add_to_dev_list(devices)

    def len(self) -> int:
        """Return the number of managed devices."""
        return len(self._items)

    def get_device_at(self, index: int) -> DeviceAccess:
        """Return the managed device at ``index``."""
        return self._items[index]

    def set(self, value: npt.NDArray[np.float64]):
        """Set all managed devices from a one-dimensional value array."""
        if len(value) != len(self._items):
            raise PyAMLException(
                f"Size of value ({len(value)} do not match the number of managed devices ({len(self._items)})"
            )

        d: FloatSignalContainer
        requests = []  # list of status to await
        for idx, d in enumerate(self._items):
            requests.append(d.SP._complete_set(value[idx]))
        arun(asyncio.gather(*requests))

    def set_and_wait(self, value: npt.NDArray[np.float64]):
        """Set all devices and wait for completion.

        Raises
        ------
        NotImplementedError
            This operation is not implemented.
        """
        raise NotImplementedError("Not implemented yet.")

    def _read(self, signal_list: dict) -> npt.NDArray[np.float64]:
        requests = []  # list of status to await
        for _d, dc in signal_list.items():
            requests.append(dc["source"].async_get())
        values = arun(asyncio.gather(*requests))
        rvalues = np.zeros(len(self._items))
        sIdx = 0
        for _, dc in signal_list.items():
            for i in dc["indices"]:
                if i[0] is None:
                    rvalues[i[1]] = values[sIdx]  # non indexed scalar value
                else:
                    rvalues[i[1]] = values[sIdx][i[0]]
            sIdx += 1

        return rvalues

    def get(self) -> npt.NDArray[np.float64]:
        """Return current setpoint values, or readbacks for read-only devices."""
        if self._writable:
            return self._read(self._w_signal_list)
        else:
            return self._read(self._r_signal_list)

    def readback(self) -> np.array:
        """Return current readback values for all managed devices."""
        return self._read(self._r_signal_list)

    def get_range(self) -> list[float]:
        """Return concatenated ranges for all managed devices."""
        attr_range: list[float] = []
        for device in self._items:
            attr_range.extend(device.get_range())
        return attr_range

    def unit(self) -> list[str]:
        """Return units in managed-device order."""
        return [a.unit() for a in self._items]

    def check_device_availability(self) -> bool:
        """Return whether every managed device is available."""
        available = False
        for device in self._items:
            available = device.check_device_availability()
            if not available:
                break
        return available

    def __repr__(self):
        ret_str = "OAScalarAggregator(\n"
        for d in self._items:
            ret_str += repr(d)
            ret_str += "\n"
        ret_str += ")"
        return ret_str

import asyncio

import numpy as np
from numpy import typing as npt
from pyaml import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess
from pyaml.control.deviceaccesslist import DeviceAccessList
from pydantic import BaseModel

from . import arun
from .float_signal import FloatSignalContainer

PYAMLCLASS: str = "OAScalarAggregator"


class ConfigModel(BaseModel):
    pass


class OAScalarAggregator(DeviceAccessList):
    def __init__(self, cfg: ConfigModel = None):
        super().__init__()
        self._r_signal_list = {} # List of signal to read
        self._w_signal_list = {} # List of signal to read/write
        self._writable = None

    def _add_to_dev_list(self,d:FloatSignalContainer):

        # Check type and read/write
        if not isinstance(d,FloatSignalContainer):
            raise PyAMLException("All devices must be instances of FloatSignalContainer.")

        if self._writable is None:
            self._writable = d._writable
        else:
            if self._writable != d._writable:
                raise PyAMLException("Cannot mix read only and read/write signal in a same aggreagator")

        # Construct structure to avoid duplicate reading
        # The shared part is the source Ophyd signal
        if d.RB._r_sig not in self._r_signal_list:
            self._r_signal_list[d.RB._r_sig] = {"source":d.RB,"indices":[[d._cfg.index,len(self)]]}
        else:
            self._r_signal_list[d.RB._r_sig]["indices"].append([d._cfg.index,len(self)])

        if self._writable:
            if d.SP._w_sig not in self._w_signal_list:
                self._w_signal_list[d.SP._w_sig] = {"source":d.SP,"indices":[[d._cfg.index,len(self)]]}
            else:
                self._w_signal_list[d.SP._w_sig]["indices"].append([d._cfg.index,len(self)])

        self.append(d)

    def add_devices(self, devices: DeviceAccess | list[DeviceAccess]):
        if isinstance(devices, list):
            for d in devices:
                self._add_to_dev_list(d)
        else:
            self._add_to_dev_list(devices)

    def get_devices(self) -> DeviceAccess | list[DeviceAccess]:
        if len(self) == 1:
            return self[0]
        else:
            return self

    def set(self, value: npt.NDArray[np.float64]):

        if len(value) != len(self):
            raise PyAMLException(f"Size of value ({len(value)} do not match the number of managed devices ({len(self)})")

        d: FloatSignalContainer
        requests = []  # list of status to await
        for idx, d in enumerate(self):
            requests.append(d.SP._complete_set(value[idx]))
        arun(asyncio.gather(*requests))

    def set_and_wait(self, value: npt.NDArray[np.float64]):
        raise NotImplementedError("Not implemented yet.")

    def _read(self,signal_list:dict) -> npt.NDArray[np.float64]:

        requests = [] # list of status to await
        for _d,dc in signal_list.items():
            requests.append( dc["source"].async_get() )
        values = arun(asyncio.gather(*requests))
        rvalues = np.zeros(len(self))
        sIdx = 0
        for _,dc in signal_list.items():
            for i in dc["indices"]:
                if i[0] is None:
                    rvalues[i[1]] = values[sIdx] # non indexed scalar value
                else:
                    rvalues[i[1]] = values[sIdx][i[0]]
            sIdx+=1

        return rvalues

    def get(self) -> npt.NDArray[np.float64]:

        if self._writable:
            return self._read(self._w_signal_list)
        else:
            return self._read(self._r_signal_list)

    def readback(self) -> np.array:

        return self._read(self._r_signal_list)

    def get_range(self) -> list[float]:
        attr_range: list[float] = []
        for device in self:
            attr_range.extend(device.get_range())
        return attr_range

    def check_device_availability(self) -> bool:
        available = False
        for device in self:
            available = device.check_device_availability()
            if not available:
                break
        return available

    def __repr__(self):
        ret_str = "OAScalarAggregator(\n"
        for d in self:
            ret_str += repr(d)
            ret_str += "\n"
        ret_str += ")"
        return ret_str

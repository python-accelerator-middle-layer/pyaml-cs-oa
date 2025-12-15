import numpy as np
from numpy import typing as npt
from pyaml.control.deviceaccess import DeviceAccess
from pydantic import BaseModel
from pyaml.control.deviceaccesslist import DeviceAccessList

from .core import FloatSignalContainer
from . import arun

import asyncio

PYAMLCLASS : str = "OAScalarAggregator"


class ConfigModel(BaseModel):
    pass

class OAScalarAggregator(DeviceAccessList):

    def __init__(self, cfg:ConfigModel=None):
        super().__init__()

    def add_devices(self, devices: DeviceAccess | list[DeviceAccess]):
        if isinstance(devices, list):
            if any([not isinstance(device, FloatSignalContainer) for device in devices]):
                raise pyaml.PyAMLException("All devices must be instances of FloatSignalContainer.")
            super().extend(devices)
        else:
            if not isinstance(devices, FloatSignalContainer):
                raise pyaml.PyAMLException("Device must be an instance of FloatSignalContainer.")
            super().append(devices)

    def get_devices(self) -> DeviceAccess | list[DeviceAccess]:
        if len(self)==1:
            return self[0]
        else:
            return self


    def set(self, value: npt.NDArray[np.float64]):
        
        if len(value)!=len(self):
            raise pyaml.PyAMLException(f"Size of value ({len(value)} do not match the number of managed devices ({len(self)})")
        
        d: FloatSignalContainer
        requests = [] # list of status to await
        for idx,d in enumerate(self):
            requests.append( d.SP._complete_set(value[idx]) )
        arun(asyncio.gather(*requests))

    def set_and_wait(self, value: npt.NDArray[np.float64]):
        raise NotImplemented("Not implemented yet.")

    def get(self) -> npt.NDArray[np.float64]:

        d: FloatSignalContainer
        requests = [] # list of status to await
        for d in self:
            if d._writable:
                requests.append( d.SP.async_get() )
            else:
                requests.append( d.RB.async_get() )
        values = arun(asyncio.gather(*requests))
        return np.array(values)

    def readback(self) -> np.array:

        d: FloatSignalContainer
        requests = [] # list of status to await
        for d in self:
            requests.append( d.RB.async_get() )
        values = arun(asyncio.gather(*requests))
        return np.array(values)

    def __repr__(self):
       return repr(self._cfg).replace("ConfigModel",self.__class__.__name__)
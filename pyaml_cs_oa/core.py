from pyaml.control.deviceaccess import DeviceAccess
from pydantic import BaseModel

from .pool import global_pool

from .types import (
    ControlSysConfig,
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
    TangoConfigR,
    TangoConfigRW,
)

class FloatSignalContainer(DeviceAccess):
    """
    Class that implements a PyAML Float Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig):
        self._cfg = cfg
        self._unit = cfg.unit

    def connect(self,timeout_ms:int):

        self._readable: bool = isinstance(
            self._cfg, (EpicsConfigR, TangoConfigR)
        )
        self._writable: bool = isinstance(
            self._cfg, (EpicsConfigRW, EpicsConfigW, TangoConfigRW)
        )
        self.SP, self.RB = global_pool._create_setpoint_readback(self.get_cs(), self._cfg,timeout_ms)

    def get_cs(self) -> str:
        raise Exception("get_cs() not implemented")

    def name(self) -> str:
        """
        Return the name of the signal.
        """
        return self._signal.name

    def measure_name(self) -> str:
        """
        Return the short attribute name (last component).

        Returns
        -------
        str
            The attribute name (e.g., 'current').
        """

        # TODO override measure name in sub classes
        if isinstance(self._cfg, (EpicsConfigR, EpicsConfigRW)):
            return self._cfg.read_pvname
        elif isinstance(self._cfg, (TangoConfigR, TangoConfigRW)):
            return self._cfg.attribute
        else:
            raise ValueError(
                f"Unsupported control system config type: {type(self._cfg)!r}"
            )

    def unit(self) -> str:
        """
        Return the unit of the attribute.

        Returns
        -------
        str
            The unit string.
        """
        return self._cfg.unit

    def get(self) -> float:
        """
        Get the last written value of the attribute.

        Returns
        -------
        float
            The last written value.

        """
        if self._writable:
            return self.SP.get()
        else:
            return self.RB.get()

    def readback(self) -> float:
        """
        Return the readback value with metadata.

        Returns
        -------
        Value
            The readback value including quality and timestamp.

        """
        return self.RB.get()

    def set(self, value: float):
        """
        Write a value asynchronously to the Tango attribute.

        Parameters
        ----------
        value : float
            Value to write to the attribute.

        """
        return self.SP.set(value)

    def set_and_wait(self, value: float):
        """
        Write a value synchronously to the Tango attribute.

        Parameters
        ----------
        value : float
            Value to write to the attribute.

        """
        self.SP.set_and_wait(value)

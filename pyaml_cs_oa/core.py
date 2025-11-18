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
    TangoConfigW,
)


class ConfigModel(BaseModel):
    cs_config: ControlSysConfig
    unit: str = ""


class FloatSignalContainer(DeviceAccess):
    """
    Class that implements a PyAML Float Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ConfigModel):
        self._cfg = cfg
        self._unit = cfg.unit
        cs_cfg = cfg.cs_config
        if isinstance(cs_cfg, (EpicsConfigRW, EpicsConfigR)):
            self._cs_name = "epics"
        elif isinstance(cs_cfg, (TangoConfigRW, TangoConfigR)):
            self._cs_name = "tango"
        else:
            raise ValueError("Unsupported control system config type")
        self._readable: bool = isinstance(
            cs_cfg, (EpicsConfigRW, EpicsConfigR, TangoConfigRW, TangoConfigR)
        )
        self._writable: bool = isinstance(
            cs_cfg, (EpicsConfigRW, EpicsConfigW, TangoConfigRW, TangoConfigW)
        )

        self.SP, self.RB = global_pool.get(self._cs_name, cfg.cs_config)

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

        cs_cfg = self._cfg.cs_config

        if isinstance(cs_cfg, (EpicsConfigR, EpicsConfigRW)):
            return cs_cfg.read_pvname
        elif isinstance(cs_cfg, (TangoConfigR, TangoConfigRW)):
            return cs_cfg.read_attr
        else:
            raise ValueError(
                f"Unsupported control system config type: {type(cs_cfg)!r}"
            )

    def unit(self) -> str:
        """
        Return the unit of the attribute.

        Returns
        -------
        str
            The unit string.
        """
        return self._unit

    def get(self) -> float:
        """
        Get the last written value of the attribute.

        Returns
        -------
        float
            The last written value.

        """
        return self.SP.get()

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

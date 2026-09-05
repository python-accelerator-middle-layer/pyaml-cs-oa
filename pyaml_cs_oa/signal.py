"""Base signal adapter shared by EPICS and Tango implementations."""

from pyaml.control.deviceaccess import DeviceAccess

from .types import (
    ControlSysConfig,
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
    TangoConfigAtt,
)


class OASignal(DeviceAccess):
    """
    Class that implements a PyAML Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig):
        self._cfg = cfg

    def build(self):
        """Create backend readback and setpoint adapters for this signal."""
        self._readable: bool = isinstance(self._cfg, (EpicsConfigR, TangoConfigAtt))
        self._writable: bool = isinstance(self._cfg, (EpicsConfigRW, EpicsConfigW, TangoConfigAtt))

        cs_name = self.get_cs()
        if cs_name == "tango":
            from .tango import get_SP_RB
        elif cs_name == "epics":
            from .epics import get_SP_RB
        else:
            raise ValueError(f"Unsupported cs_name: {cs_name}")

        self.SP, self.RB = get_SP_RB(self._cfg)

        if self.SP:
            self.SP.__peer__ = self
        if self.RB:
            self.RB.__peer__ = self

    def get_cs(self) -> str:
        """Return the backend identifier implemented by the subclass."""
        raise Exception("get_cs() not implemented")

    def name(self) -> str:
        """Return the backend signal name."""
        return self._signal.name

    def measure_name(self) -> str:
        """Return the configured process-variable or attribute name."""
        if isinstance(self._cfg, (EpicsConfigR, EpicsConfigRW)):
            return self._cfg.read_pvname
        elif isinstance(self._cfg, EpicsConfigW):
            return self._cfg.write_pvname
        elif isinstance(self._cfg, TangoConfigAtt):
            return self._cfg.attribute
        else:
            raise ValueError(f"Unsupported control system config type: {type(self._cfg)!r}")

    def unit(self) -> str:
        """Return the configured engineering unit."""
        return self._cfg.unit

    def get_range(self) -> list:
        """Return the configured numeric range, if any."""
        if isinstance(self._cfg, (EpicsConfigW, EpicsConfigRW, TangoConfigAtt)):
            if self._cfg.range:
                return self._cfg.range
        return [None, None]

    def check_device_availability(self) -> bool:
        """Return whether the device is available.

        Notes
        -----
        The current implementation does not perform an active health check.
        """
        # TODO
        return True

    def __repr__(self):
        cfg_str = repr(self._cfg)
        idx = cfg_str.find("(")
        return f"{self.__class__.__name__}{cfg_str[idx:]}"

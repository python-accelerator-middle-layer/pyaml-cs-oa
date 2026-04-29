from pyaml.control.deviceaccess import DeviceAccess

from .types import (
    ControlSysConfig,
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
    TangoConfigR,
    TangoConfigRW,
)

class OASignal(DeviceAccess):
    """
    Class that implements a PyAML Signal using ophyd_async Signals.
    """

    def __init__(self, cfg: ControlSysConfig, is_array: bool = False):
        self._cfg = cfg
        # is_array is forced True whenever any index is specified.
        self.is_array = is_array or cfg.index is not None

    def build(self):
        self._readable: bool = isinstance(self._cfg, (EpicsConfigR, TangoConfigR))
        self._writable: bool = isinstance(
            self._cfg, (EpicsConfigRW, EpicsConfigW, TangoConfigRW)
        )

        cs_name = self.get_cs()
        if cs_name == "tango":
            from .tango import get_SP_RB
        elif cs_name == "epics":
            from .epics import get_SP_RB
        else:
            raise ValueError(f"Unsupported cs_name: {cs_name}")

        self.SP, self.RB = get_SP_RB(self._cfg, self.is_array)

        if self.SP:
            self.SP.__peer__ = self
        if self.RB:
            self.RB.__peer__ = self

    def get_cs(self) -> str:
        raise Exception("get_cs() not implemented")

    def name(self) -> str:
        return self._signal.name

    def measure_name(self) -> str:
        if isinstance(self._cfg, (EpicsConfigR, EpicsConfigRW)):
            base = self._cfg.read_pvname
        elif isinstance(self._cfg, EpicsConfigW):
            base = self._cfg.write_pvname
        elif isinstance(self._cfg, (TangoConfigR, TangoConfigRW)):
            base = self._cfg.attribute
        else:
            raise ValueError(
                f"Unsupported control system config type: {type(self._cfg)!r}"
            )
        eff_read, _ = _effective_indexes(self._cfg)
        return f"{base}[{eff_read}]" if eff_read is not None else base

    def unit(self) -> str:
        return self._cfg.unit

    def get_range(self) -> list:
        if self._writable and self._cfg.range:
            return self._cfg.range
        else:
            return [None, None]

    def check_device_availability(self) -> bool:
        #TODO
        return True

    def __repr__(self):
       cfg_str = repr(self._cfg)
       idx = cfg_str.find("(")
       return f"{self.__class__.__name__}{cfg_str[idx:]}"

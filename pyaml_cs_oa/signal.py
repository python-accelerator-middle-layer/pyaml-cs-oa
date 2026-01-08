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

    def __init__(self, cfg: ControlSysConfig):
        self._cfg = cfg

    def build(self):

        self._readable: bool = isinstance(
            self._cfg, (EpicsConfigR, TangoConfigR)
        )
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

        self.SP, self.RB = get_SP_RB(self._cfg)
        if self.SP:
            self.SP.__peer__ = self
        if self.RB:
            self.RB.__peer__ = self

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

    def __repr__(self):
       return repr(self._cfg).replace("ConfigModel",self.__class__.__name__)

import logging

from pyaml.common.element import __pyaml_repr__
from pyaml.common.exception import PyAMLException
from pyaml.control.controlsystem import ControlSystem
from pyaml.control.deviceaccess import DeviceAccess
from pyaml.control.deviceaccesslist import DeviceAccessList
from pyaml.validation import DynamicValidation, register_schema
from pydantic import BaseModel

from . import __version__
from .aggregator import OAAggregator
from .catalog import Catalog
from .epicsR import EpicsR
from .epicsRW import EpicsRW
from .epicsW import EpicsW
from .signal import OASignal
from .tangoAtt import TangoAtt
from .types import ControlSysConfig, EpicsConfigR, EpicsConfigRW, EpicsConfigW, TangoConfigAtt

PYAMLCLASS: str = "OphydAsyncControlSystem"

logger = logging.getLogger(__name__)


@register_schema
class OphydAsyncControlSystem(ControlSystem, DynamicValidation):
    """A generic control system using ophyd_async backend.

    Attributes
    ----------
    name : str
        Name of the control system.
    prefix : str
        Prefix added to the PV or attribute name. It can be a
        for instance, TANGO_HOST, or a PV prefix.
    catalog : Catalog | None
        Catalog instance or catalog name used to resolve PyAML device keys.
        If None specified a dynamic catalog is used.
    debug_level : str | int | None
        Debug verbosity level.
    """

    def __init__(self, name: str, prefix: str = "", catalog: Catalog | None = None, debug_level: str | int | None = None):
        super().__init__()
        self._name = name
        self._prefix = prefix
        self._catalog = catalog
        self.debug_level = debug_level

        self._devices: dict[str, DeviceAccess] = {}  # Dict containing all attached DeviceAccess

        if self.debug_level:
            if isinstance(self.debug_level, str):
                log_level = getattr(logging, self.debug_level.upper(), logging.WARNING)
            else:
                log_level = self.debug_level
            logger.setLevel(log_level)

        logger.log(
            logging.WARNING,
            f"PyAML OA control system binding ({__version__}) initialized with name '{self.name}' and prefix='{self.prefix}'",
        )

    def attach(self, devs: list[OASignal | None]) -> list[OASignal | None]:
        # Deprecated function
        return self._attach([d._cfg if d is not None else None for d in devs])

    def attach_array(self, devs: list[OASignal | None]) -> list[OASignal | None]:
        # Deprecated function
        return self._attach([d._cfg if d is not None else None for d in devs])

    def get_device_access(self, ref: str | BaseModel | None) -> DeviceAccess | None:
        if ref is None:
            return None

        if isinstance(ref, str):
            # Retrieve a config from a key using using a Catalog
            if self._catalog is None:
                raise PyAMLException(f"Control system '{self.name()}' has no catalog when trying to resolve '{ref}'")
            try:
                ref = self._catalog.resolve(ref)
            except AttributeError as exc:
                raise PyAMLException(f"Control system '{self.name()}' catalog cannot resolve key '{ref}'") from exc

        if isinstance(ref, EpicsConfigR):
            return self._attach([ref])[0]
        if isinstance(ref, EpicsConfigW):
            return self._attach([ref])[0]
        if isinstance(ref, EpicsConfigRW):
            return self._attach([ref])[0]
        if isinstance(ref, TangoConfigAtt):
            return self._attach([ref])[0]

        raise PyAMLException(f"Control system '{self.name()}' cannot build a device from {type(ref).__name__}")

    def _attach(self, configs: list[ControlSysConfig | None]) -> list[OASignal | None]:
        # Concatenate the prefix
        newDevs = []
        for sig_cfg in configs:
            if sig_cfg is not None:
                sig_cfg_cls = sig_cfg.__class__
                index_str = "" if sig_cfg.index is None else str(sig_cfg.index)

                if isinstance(sig_cfg, EpicsConfigR):
                    key = self.prefix + sig_cfg.read_pvname + index_str
                    sig_cls = EpicsR
                    config = dict(read_pvname=self.prefix + sig_cfg.read_pvname)
                elif isinstance(sig_cfg, EpicsConfigW):
                    key = self.prefix + sig_cfg.write_pvname + index_str
                    sig_cls = EpicsW
                    config = dict(write_pvname=self.prefix + sig_cfg.write_pvname)
                elif isinstance(sig_cfg, EpicsConfigRW):
                    key = self.prefix + sig_cfg.read_pvname + sig_cfg.write_pvname + index_str
                    sig_cls = EpicsRW
                    config = dict(
                        read_pvname=self.prefix + sig_cfg.read_pvname,
                        write_pvname=self.prefix + sig_cfg.write_pvname,
                    )
                elif isinstance(sig_cfg, TangoConfigAtt):
                    key = self.prefix + sig_cfg.attribute + index_str
                    sig_cls = TangoAtt
                    config = dict(attribute=self.prefix + sig_cfg.attribute)
                else:
                    raise PyAMLException(f"OphydAsyncControlSystem: Unsupported type {type(sig_cfg)}")

                if key not in self._devices:
                    n_conf = dict(sig_cfg) | config
                    nr = sig_cls(sig_cfg_cls(**n_conf))
                    nr.build()
                    self._devices[key] = nr

                newDevs.append(self._devices[key])
            else:
                newDevs.append(None)
        return newDevs

    def name(self) -> str:
        """
        Return the name of the control system.

        Returns
        -------
        str
            Name of the control system.
        """
        return self._name

    @property
    def prefix(self) -> str:
        """
        Return the prefix of the control system.

        Returns
        -------
        str
            Prefix of the control system.
        """
        return self._prefix

    def get_aggregator(self) -> DeviceAccessList | None:
        """Returns a new empty DeviceAccessList. If None is returned serialized readings/writtings are performed"""
        return OAAggregator()

    def __repr__(self):
        return __pyaml_repr__(self)

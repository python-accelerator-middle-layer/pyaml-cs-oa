import logging

from pydantic import BaseModel, ConfigDict
from pyaml.common.exception import PyAMLException
from pyaml.configuration.catalog import Catalog
from pyaml.control.controlsystem import ControlSystem

PYAMLCLASS: str = "OphydAsyncControlSystem"

logger = logging.getLogger(__name__)

from . import __version__
from .epicsR import EpicsR
from .epicsRW import EpicsRW
from .epicsW import EpicsW
from .signal import OASignal
from .tangoR import TangoR
from .tangoRW import TangoRW
from .types import (
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
    TangoConfigR,
    TangoConfigRW,
)

PYAMLCLASS: str = "OphydAsyncControlSystem"

logger = logging.getLogger(__name__)

class ConfigModel(BaseModel):
    """
    Configuration model for an OA Control System.

    Attributes
    ----------
    name : str
        Name of the control system.
    prefix : str
        Prefix added to the PV or attribute name. It can be a
        for instance, TANGO_HOST, or a PV prefix.
    catalog : Catalog | str | None
        Catalog instance or catalog name used to resolve PyAML device keys.
    debug_level : str
        Debug verbosity level.
    scalar_aggregator : str
        Aggregator module for scalar values. If none specified, writings and
        readings of sclar value are serialized.
    vector_aggregator : str
        Aggregator module for vecrors. If none specified, writings and readings
        of vector are serialized,
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    name: str
    prefix: str = ""
    catalog: Catalog | str | None = None
    debug_level: str | None = None
    scalar_aggregator: str | None = "pyaml_cs_oa.scalar_aggregator"
    vector_aggregator: str | None = None


class OphydAsyncControlSystem(ControlSystem):
    """A generic control system using ophyd_async backend."""

    def __init__(self, cfg: ConfigModel):
        super().__init__()
        self._cfg = cfg
        self._devices = {}  # Dict containing all attached DeviceAccess

        if self._cfg.debug_level:
            log_level = getattr(logging, self._cfg.debug_level, logging.WARNING)
            logger.parent.setLevel(log_level)
            logger.setLevel(log_level)

        logger.log(
            logging.WARNING,
            f"PyAML OA control system binding ({__version__}) initialized with name '{self._cfg.name}'"
            f" and prefix='{self._cfg.prefix}'",
        )

    def attach(self, devs: list[OASignal | None]) -> list[OASignal | None]:
        return self._attach(devs, False)

    def attach_array(self, devs: list[OASignal | None]) -> list[OASignal | None]:
        return self._attach(devs, True)

    def _attach(self, devs: list[OASignal | None], is_array: bool) -> list[OASignal | None]:
        # Concatenate the prefix
        newDevs = []
        for d in devs:
            if d is not None:
                sig_cfg = d._cfg
                sig_cfg_cls = sig_cfg.__class__
                index_str = "" if sig_cfg.index is None else str(sig_cfg.index)

                if isinstance(d._cfg, EpicsConfigR):
                    key = self._cfg.prefix + d._cfg.read_pvname + index_str
                    sig_cls = EpicsR
                    config = dict(read_pvname=self._cfg.prefix + d._cfg.read_pvname)
                elif isinstance(d._cfg, EpicsConfigW):
                    key = self._cfg.prefix + d._cfg.write_pvname + index_str
                    sig_cls = EpicsW
                    config = dict(write_pvname=self._cfg.prefix + d._cfg.write_pvname)
                elif isinstance(d._cfg, EpicsConfigRW):
                    key = self._cfg.prefix + d._cfg.read_pvname + d._cfg.write_pvname + index_str
                    sig_cls = EpicsRW
                    config = dict(
                        read_pvname=self._cfg.prefix + d._cfg.read_pvname,
                        write_pvname=self._cfg.prefix + d._cfg.write_pvname,
                    )
                elif isinstance(d._cfg, TangoConfigR):
                    key = self._cfg.prefix + d._cfg.attribute + index_str
                    sig_cls = TangoR
                    config = dict(attribute=self._cfg.prefix + d._cfg.attribute)
                elif isinstance(d._cfg, TangoConfigRW):
                    key = self._cfg.prefix + d._cfg.attribute + index_str
                    sig_cls = TangoRW
                    config = dict(attribute=self._cfg.prefix + d._cfg.attribute)
                else:
                    raise PyAMLException(f"OphydAsyncControlSystem: Unsupported type {type(sig_cfg)}")

                if key not in self._devices:
                    n_conf = dict(d._cfg) | config
                    nr = sig_cls(sig_cfg_cls(**n_conf), is_array)
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
        return self._cfg.name

    def scalar_aggregator(self) -> str | None:
        """
        Returns the module name used for handling aggregator of DeviceAccess

        Returns
        -------
        str
            Aggregator module name
        """
        return self._cfg.scalar_aggregator

    def vector_aggregator(self) -> str | None:
        """
        Returns the module name used for handling aggregator of DeviceVectorAccess

        Returns
        -------
        str
            Aggregator module name
        """
        return self._cfg.vector_aggregator

    def __repr__(self):
        return repr(self._cfg).replace("ConfigModel", self.__class__.__name__)

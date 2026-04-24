from pydantic import ConfigDict

from pyaml.common.exception import PyAMLException
from pyaml.configuration.catalog import Catalog, CatalogConfigModel
from pyaml.control.deviceaccess import DeviceAccess

from .epics_static_catalog_entry import EpicsStaticCatalogEntry

PYAMLCLASS = "EpicsStaticCatalog"


class ConfigModel(CatalogConfigModel):
    """
    Static EPICS catalog — ordered list of typed entries.

    Each entry is an ``EpicsStaticCatalogEntry`` whose ``device`` is one of
    ``EpicsR``, ``EpicsW``, or ``EpicsRW``.  Index fields on the device config
    control array-element access:

    * ``index`` — common index applied to both read and write sides of ``EpicsRW``.
    * ``read_index`` / ``write_index`` — per-side overrides (``EpicsRW`` only).

    Example
    -------
    .. code-block:: yaml

        type: pyaml_cs_oa.epics_static_catalog
        name: device-catalog
        entries:
          - type: pyaml_cs_oa.epics_static_catalog_entry
            key: magnet_current
            device:
              type: pyaml_cs_oa.epicsRW
              read_pvname: HS4P2D1R:rdbk
              write_pvname: HS4P2D1R:set
              unit: A
          - type: pyaml_cs_oa.epics_static_catalog_entry
            key: id_gap
            device:
              type: pyaml_cs_oa.epicsRW
              read_pvname: R:GAP:ALL_ID
              write_pvname: W:GAP:ID_SET
              read_index: 24
              write_index: 30
              unit: mm
          - type: pyaml_cs_oa.epics_static_catalog_entry
            key: phase
            device:
              type: pyaml_cs_oa.epicsR
              read_pvname: R:PHASE:ALL
              index: 24
              unit: mm
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    entries: list[EpicsStaticCatalogEntry]


class EpicsStaticCatalog(Catalog):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
        if not cfg.entries:
            raise PyAMLException(
                "EpicsStaticCatalog.entries must contain at least one entry"
            )
        self._refs: dict[str, DeviceAccess] = {}
        for entry in cfg.entries:
            key = entry.get_key()
            if key in self._refs:
                raise PyAMLException(
                    f"EpicsStaticCatalog '{self.get_name()}': duplicate key '{key}'"
                )
            sig = entry.get_device()
            sig.build()
            self._refs[key] = sig

    def resolve(self, key: str) -> DeviceAccess:
        try:
            return self._refs[key]
        except KeyError as exc:
            raise PyAMLException(
                f"Catalog '{self.get_name()}' cannot resolve key '{key}'"
            ) from exc

from pyaml.common.exception import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess
from pydantic import BaseModel, ConfigDict

from .catalog import Catalog
from .static_catalog_entry import StaticCatalogEntry

PYAMLCLASS = "StaticCatalog"


class ConfigModel(BaseModel):
    """
    Static catalog: a fixed mapping of keys to DeviceAccess instances.
    Keys are resolved at construction time; no control-system connection is required.
    The catalog instance is shared across all control systems that reference it.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    entries: list[StaticCatalogEntry]


class StaticCatalog(Catalog):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
        if not cfg.entries:
            raise PyAMLException("StaticCatalog.entries must contain at least one entry")
        self._refs: dict[str, DeviceAccess] = {}
        for entry in cfg.entries:
            key = entry.get_key()
            if key in self._refs:
                raise PyAMLException(f"StaticCatalog.entries contains duplicate key '{key}'")
            self._refs[key] = entry.get_device()

    def resolve(self, key: str) -> BaseModel:
        try:
            return self._refs[key]._cfg
        except KeyError as exc:
            raise PyAMLException(f"Catalog '{self.get_name()}' cannot resolve key '{key}'") from exc

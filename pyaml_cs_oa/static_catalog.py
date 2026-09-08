"""Fixed-key catalog implementation for configured devices."""

from pyaml.common.exception import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess
from pyaml.validation import DynamicValidation, register_schema
from pydantic import BaseModel

from .catalog import Catalog
from .static_catalog_entry import StaticCatalogEntry

PYAMLCLASS = "StaticCatalog"


@register_schema
class StaticCatalog(Catalog, DynamicValidation):
    """
    Static catalog: a fixed mapping of keys to DeviceAccess instances.
    Keys are resolved at construction time; no control-system connection is required.
    The catalog instance is shared across all control systems that reference it.
    """

    def __init__(self, entries: list[StaticCatalogEntry]):
        self._entries = entries

        if not self._entries:
            raise PyAMLException("StaticCatalog.entries must contain at least one entry")
        self._refs: dict[str, DeviceAccess] = {}
        for entry in self._entries:
            key = entry.get_key()
            if key in self._refs:
                raise PyAMLException(f"StaticCatalog.entries contains duplicate key '{key}'")
            self._refs[key] = entry.get_device()

    def resolve(self, key: str) -> BaseModel:
        """Resolve ``key`` to its device configuration model."""
        try:
            return self._refs[key]._cfg
        except KeyError as exc:
            raise PyAMLException(f"StaticCatalog cannot resolve key '{key}'") from exc

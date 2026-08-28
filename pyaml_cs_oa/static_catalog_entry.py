"""Configuration entries used by the static catalog."""

from pyaml.control.deviceaccess import DeviceAccess
from pydantic import BaseModel, ConfigDict

PYAMLCLASS = "StaticCatalogEntry"


class ConfigModel(BaseModel):
    """Configuration for one named device reference."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    key: str
    device: DeviceAccess


class StaticCatalogEntry:
    """Resolved key-to-device entry used by :class:`StaticCatalog`."""

    def __init__(self, cfg: ConfigModel):
        self._cfg = cfg

    def get_key(self) -> str:
        """Return the catalog key."""
        return self._cfg.key

    def get_device(self) -> DeviceAccess:
        """Return the configured device."""
        return self._cfg.device

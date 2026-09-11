"""Configuration entries used by the static catalog."""

from pyaml.control.deviceaccess import DeviceAccess
from pyaml.validation import DynamicValidation, register_schema

PYAMLCLASS = "StaticCatalogEntry"


@register_schema
class StaticCatalogEntry(DynamicValidation):
    """Resolved key-to-device entry used by :class:`StaticCatalog`."""

    def __init__(self, key: str, device: DeviceAccess):
        self.key = key
        self.device = device

    def get_key(self) -> str:
        """Return the catalog key."""
        return self.key

    def get_device(self) -> DeviceAccess:
        """Return the configured device."""
        return self.device

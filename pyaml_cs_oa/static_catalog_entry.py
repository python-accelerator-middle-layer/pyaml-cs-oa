from pyaml.control.deviceaccess import DeviceAccess
from pyaml.validation import DynamicValidation, register_schema

PYAMLCLASS = "StaticCatalogEntry"


@register_schema
class StaticCatalogEntry(DynamicValidation):
    def __init__(self, key: str, device: DeviceAccess):
        self._key = key
        self._device = device

    def get_key(self) -> str:
        return self._key

    def get_device(self) -> DeviceAccess:
        return self._device

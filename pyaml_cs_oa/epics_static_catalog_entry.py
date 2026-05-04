from pyaml.control.deviceaccess import DeviceAccess
from pydantic import BaseModel, ConfigDict

PYAMLCLASS = "EpicsStaticCatalogEntry"


class ConfigModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    key: str
    device: DeviceAccess  # EpicsR, EpicsW, or EpicsRW instance (build() not yet called)


class EpicsStaticCatalogEntry:
    def __init__(self, cfg: ConfigModel):
        self._cfg = cfg

    def get_key(self) -> str:
        return self._cfg.key

    def get_device(self) -> DeviceAccess:
        return self._cfg.device

from dataclasses import dataclass
import json
import hashlib
from pydantic import BaseModel

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import ControlSysConfig

def get_pydantic_model_hash(model: BaseModel) -> str:

    d = model.model_dump(mode="json")
    data_bytes = json.dumps(d, sort_keys=True, indent=None).encode()

    h = hashlib.sha256(data_bytes).hexdigest()[:16]
    return h

@dataclass(frozen=True)
class _ContainerKey:
    cs_name: str
    cfg_hash: str

class OASignalContainerPool():

    def __init__(self):
        self._cache: dict[_ContainerKey, tuple[Setpoint | None, Readback | None]] = {}

    def _create_setpoint_readback(
        self, cs_name: str, cs_cfg: ControlSysConfig
    ) -> tuple[Setpoint | None, Readback | None]:
        key = self._key(cs_name, cs_cfg)

        # Lazily construct using your existing backend helpers
        if cs_name == "tango":
            from .tango import get_SP_RB
        elif cs_name == "epics":
            from .epics import get_SP_RB
        else:
            raise ValueError(f"Unsupported cs_name: {cs_name}")

        # Install a rebuild hook the recovery code can call
        def _rebuild():
            new_SP, new_RB = get_SP_RB(cs_cfg)
            self._cache[key] = (new_SP, new_RB)
            # carry the hook forward
            for v in (new_SP, new_RB):
                if v is not None:
                    v.__rebuild__ = _rebuild

        setpoint, readback = get_SP_RB(cs_cfg)
        for v in (setpoint, readback):
            if v is not None:
                v.__rebuild__ = _rebuild
        self._cache[key] = (setpoint, readback)

        return setpoint, readback

    def _key(self, cs_name: str, cs_cfg: ControlSysConfig) -> _ContainerKey:
        return _ContainerKey(cs_name, get_pydantic_model_hash(cs_cfg))


global_pool = OASignalContainerPool()

from pyaml.control.signal.pool import SignalContainerPool

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import ControlSysConfig


class OASignalContainerPool(SignalContainerPool):
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


global_pool = OASignalContainerPool()

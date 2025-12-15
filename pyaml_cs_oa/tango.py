from ophyd_async.tango.core import tango_signal_r, tango_signal_rw

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import (
    ControlSysConfig,
    TangoConfigR,
    TangoConfigRW,
)


def get_SP_RB(cfg: ControlSysConfig,timeout_ms:int) -> tuple[Setpoint | None, Readback | None]:
    setpoint: Setpoint | None = None
    readback: Readback | None = None

    assert isinstance(cfg, (TangoConfigRW, TangoConfigR))

    if isinstance(cfg, (TangoConfigR)):
        r_sig = tango_signal_r(
            datatype=float,
            read_trl=cfg.attribute,
            timeout=timeout_ms,
        )
        readback = Readback(r_sig)
        setpoint = None

    elif isinstance(cfg, (TangoConfigRW)):
        rw_sig = tango_signal_rw(
            datatype=float,
            read_trl=cfg.attribute,
            write_trl=cfg.attribute,
            timeout=timeout_ms,
        )
        readback = Readback(rw_sig)
        setpoint = Setpoint(rw_sig)

    return setpoint, readback

from ophyd_async.tango.core import tango_signal_r, tango_signal_w

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .controlsystem import OphydAsyncCompatibleControlSystem as TangoControlSystem
from .controlsystem import (
    OphydAsyncCompatibleControlSystemConfig as TangoControlSystemConfig,
)
from .types import (
    ControlSysConfig,
    TangoConfigR,
    TangoConfigRW,
    TangoConfigW,
)


def get_SP_RB(cfg: ControlSysConfig) -> tuple[Setpoint | None, Readback | None]:
    setpoint: Setpoint | None = None
    readback: Readback | None = None

    assert isinstance(cfg, (TangoConfigRW, TangoConfigR, TangoConfigW))

    if isinstance(cfg, (TangoConfigR, TangoConfigRW)):
        r_sig = tango_signal_r(
            datatype=float,
            read_trl=cfg.read_attr,
            name="",
        )
        readback = Readback(r_sig)

    if isinstance(cfg, (TangoConfigW, TangoConfigRW)):
        w_sig = tango_signal_w(
            datatype=float,
            write_trl=cfg.write_attr,
            name="",
        )
        if isinstance(cfg, TangoConfigRW):
            setpoint = Setpoint(w_sig, r_signal=readback._r_sig if readback else None)
        else:
            setpoint = Setpoint(w_sig)

    return setpoint, readback

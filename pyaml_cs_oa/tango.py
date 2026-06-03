import numpy
from ophyd_async.core import Array1D
from ophyd_async.tango.core import tango_signal_r, tango_signal_rw

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import (
    ControlSysConfig,
    TangoConfigAtt,
)


def get_SP_RB(cfg: ControlSysConfig, is_array: bool) -> tuple[Setpoint | None, Readback | None]:
    setpoint: Setpoint | None = None
    readback: Readback | None = None

    assert isinstance(cfg, TangoConfigAtt)

    rw_sig = tango_signal_rw(
        datatype=float if not is_array else Array1D[numpy.float64],
        read_trl=cfg.attribute,
        write_trl=cfg.attribute,
        timeout=cfg.timeout_ms,
    )
    readback = Readback(rw_sig)
    setpoint = Setpoint(rw_sig)

    return setpoint, readback

"""Factories for ophyd-async Tango signals."""

import numpy
from ophyd_async.core import Array1D
from ophyd_async.tango.core import tango_signal_r, tango_signal_rw

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import (
    ControlSysConfig,
    TangoConfigAtt,
)


def get_SP_RB(cfg: ControlSysConfig) -> tuple[Setpoint | None, Readback | None]:
    """Build setpoint and readback adapters for a Tango configuration."""
    setpoint: Setpoint | None = None
    readback: Readback | None = None

    assert isinstance(cfg, TangoConfigAtt)

    rw_sig = tango_signal_rw(
        datatype=None,
        read_trl=cfg.attribute,
        write_trl=cfg.attribute,
        timeout=cfg.timeout_ms,
    )
    readback = Readback(rw_sig)
    setpoint = Setpoint(rw_sig)

    return setpoint, readback

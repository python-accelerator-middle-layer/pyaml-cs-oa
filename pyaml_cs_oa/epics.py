from ophyd_async.epics.signal import epics_signal_r, epics_signal_rw

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import (
    ControlSysConfig,
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
)


def get_SP_RB(cfg: ControlSysConfig,timeout_ms:int) -> tuple[Setpoint | None, Readback | None]:
    setpoint: Setpoint | None = None
    readback: Readback | None = None

    assert isinstance(cfg, (EpicsConfigRW, EpicsConfigR, EpicsConfigW))

    if isinstance(cfg, EpicsConfigR):
        r_sig = epics_signal_r(
            datatype=float,
            read_pv=cfg.read_pvname,
            name="",
            timeout = timeout_ms / 1000.,
        )
        readback = Readback(r_sig)
        setpoint = None

    if isinstance(cfg, EpicsConfigRW):
        w_sig = epics_signal_rw(
            datatype=float,
            read_pv=cfg.read_pvname,
            write_pv=cfg.write_pvname,
            name="",
            timeout = timeout_ms / 1000.,
        )
        readback = Readback(w_sig)
        setpoint = Setpoint(w_sig)


    return setpoint, readback

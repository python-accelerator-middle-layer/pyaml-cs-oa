from ophyd_async.epics.signal import epics_signal_r, epics_signal_w, epics_signal_rw
from ophyd_async.core import SignalR, SignalW, SignalRW

from .container import OAReadback as Readback
from .container import OASetpoint as Setpoint
from .types import (
    ControlSysConfig,
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
)

ALL_R = {}
ALL_W = {}
ALL_RW = {}

def create_signal_r(read_pv:str,timeout:float) -> SignalR:        
        if read_pv not in ALL_R:
            # Do not create same signal several times
            r_sig = epics_signal_r(
                datatype = None,
                read_pv = read_pv,
                name = read_pv,
                timeout = timeout,
            )
            ALL_R[read_pv] = r_sig
        return ALL_R[read_pv]

def create_signal_w(write_pv:str,timeout:float) -> SignalR:        
        if write_pv not in ALL_W:
            # Do not create same signal several times
            w_sig = epics_signal_w(
                datatype = None,
                write_pv = write_pv,
                name = write_pv,
                timeout = timeout,
            )
            ALL_W[write_pv] = w_sig
        return ALL_W[write_pv]

def create_signal_rw(read_pv:str,write_pv:str,timeout:float) -> SignalR:        
        key = read_pv + write_pv
        if key not in ALL_RW:
            # Do not create same signal several times
            rw_sig = epics_signal_rw(
                datatype = None,
                read_pv = read_pv,
                write_pv = write_pv,
                name = read_pv,
                timeout = timeout,
            )
            ALL_RW[key] = rw_sig
        return ALL_RW[key]

def get_SP_RB(cfg: ControlSysConfig,is_array:bool) -> tuple[Setpoint | None, Readback | None]:
    setpoint: Setpoint | None = None
    readback: Readback | None = None

    assert isinstance(cfg, (EpicsConfigRW, EpicsConfigR, EpicsConfigW))

    if isinstance(cfg, EpicsConfigR):
        r_sig = create_signal_r(cfg.read_pvname,cfg.timeout_ms / 1000.0)
        readback = Readback(r_sig,cfg.index)
        setpoint = None

    if isinstance(cfg, EpicsConfigW):
        w_sig = create_signal_w(cfg.write_pvname,cfg.timeout_ms / 1000.0)
        readback = None
        setpoint = Setpoint(w_sig,cfg.index)

    if isinstance(cfg, EpicsConfigRW):
        rw_sig = create_signal_rw(cfg.read_pvname,cfg.write_pvname,cfg.timeout_ms / 1000.0)
        readback = Readback(rw_sig,cfg.index)
        setpoint = Setpoint(rw_sig,cfg.index)


    return setpoint, readback

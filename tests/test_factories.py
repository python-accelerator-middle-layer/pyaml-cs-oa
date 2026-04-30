from __future__ import annotations

from typing import Any

import pytest

from pyaml_cs_oa import epics, tango
from pyaml_cs_oa.container import OAReadback, OASetpoint
from pyaml_cs_oa.types import (
    EpicsConfigR,
    EpicsConfigRW,
    EpicsConfigW,
    TangoConfigR,
    TangoConfigRW,
)


class SignalFactorySpy:
    """Callable recording ophyd signal constructor arguments."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> str:
        self.calls.append(kwargs)
        return self.label


def test_epics_read_only_factory_builds_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = SignalFactorySpy("epics-r")
    monkeypatch.setattr(epics, "epics_signal_r", spy)

    setpoint, readback = epics.get_SP_RB(EpicsConfigR(read_pvname="PV:RB"), False)

    assert setpoint is None
    assert isinstance(readback, OAReadback)
    assert readback._r_sig == "epics-r"
    assert spy.calls[0]["read_pv"] == "PV:RB"
    assert spy.calls[0]["timeout"] == 3.0


def test_epics_write_only_factory_builds_setpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = SignalFactorySpy("epics-w")
    monkeypatch.setattr(epics, "epics_signal_w", spy)

    setpoint, readback = epics.get_SP_RB(EpicsConfigW(write_pvname="PV:SP"), False)

    assert isinstance(setpoint, OASetpoint)
    assert readback is None
    assert setpoint._w_sig == "epics-w"
    assert spy.calls[0]["write_pv"] == "PV:SP"


def test_epics_read_write_factory_reuses_single_rw_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = SignalFactorySpy("epics-rw")
    monkeypatch.setattr(epics, "epics_signal_rw", spy)

    setpoint, readback = epics.get_SP_RB(
        EpicsConfigRW(read_pvname="PV:RB", write_pvname="PV:SP"),
        False,
    )

    assert isinstance(setpoint, OASetpoint)
    assert isinstance(readback, OAReadback)
    assert setpoint._w_sig == readback._r_sig == "epics-rw"
    assert spy.calls[0]["read_pv"] == "PV:RB"
    assert spy.calls[0]["write_pv"] == "PV:SP"


def test_tango_read_only_factory_builds_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = SignalFactorySpy("tango-r")
    monkeypatch.setattr(tango, "tango_signal_r", spy)

    setpoint, readback = tango.get_SP_RB(
        TangoConfigR(attribute="sys/tg_test/1/value"),
        False,
    )

    assert setpoint is None
    assert isinstance(readback, OAReadback)
    assert readback._r_sig == "tango-r"
    assert spy.calls[0]["read_trl"] == "sys/tg_test/1/value"


def test_tango_read_write_factory_reuses_single_rw_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = SignalFactorySpy("tango-rw")
    monkeypatch.setattr(tango, "tango_signal_rw", spy)

    setpoint, readback = tango.get_SP_RB(
        TangoConfigRW(attribute="sys/tg_test/1/value"),
        False,
    )

    assert isinstance(setpoint, OASetpoint)
    assert isinstance(readback, OAReadback)
    assert setpoint._w_sig == readback._r_sig == "tango-rw"
    assert spy.calls[0]["read_trl"] == "sys/tg_test/1/value"
    assert spy.calls[0]["write_trl"] == "sys/tg_test/1/value"

import pytest

from pyaml_cs_oa.epicsR import ConfigModel as EpicsRConfig
from pyaml_cs_oa.epicsR import EpicsR
from pyaml_cs_oa.epicsRW import ConfigModel as EpicsRWConfig
from pyaml_cs_oa.epicsW import ConfigModel as EpicsWConfig
from pyaml_cs_oa.epicsW import EpicsW
from pyaml_cs_oa.tangoAtt import ConfigModel as TangoAttConfig
from pyaml_cs_oa.tangoAtt import TangoAtt
from pyaml_cs_oa.types import EpicsConfigW


class BuiltSide:
    pass


def test_epics_signal_build_sets_peer_on_built_sides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    setpoint = BuiltSide()
    readback = BuiltSide()

    def fake_get_sp_rb(cfg):
        assert cfg.read_pvname == "PV:RB"
        assert cfg.write_pvname == "PV:SP"
        return setpoint, readback

    monkeypatch.setattr("pyaml_cs_oa.epics.get_SP_RB", fake_get_sp_rb)

    signal = EpicsR(EpicsRWConfig(read_pvname="PV:RB", write_pvname="PV:SP"))
    signal.build()

    assert signal.SP is setpoint
    assert signal.RB is readback
    assert setpoint.__peer__ is signal
    assert readback.__peer__ is signal


def test_tango_signal_build_uses_tango_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    readback = BuiltSide()

    def fake_get_sp_rb(cfg):
        assert cfg.attribute == "sys/tg_test/1/value"
        return None, readback

    monkeypatch.setattr("pyaml_cs_oa.tango.get_SP_RB", fake_get_sp_rb)

    signal = TangoAtt(TangoAttConfig(attribute="sys/tg_test/1/value"))
    signal.build()

    assert signal.SP is None
    assert signal.RB is readback
    assert readback.__peer__ is signal


def test_measure_name_uses_epics_read_pv_for_readable_signal() -> None:
    signal = EpicsR(EpicsRConfig(read_pvname="PV:RB"))

    assert signal.measure_name() == "PV:RB"


def test_measure_name_uses_tango_attribute() -> None:
    signal = TangoAtt(TangoAttConfig(attribute="sys/tg_test/1/value"))

    assert signal.measure_name() == "sys/tg_test/1/value"


def test_measure_name_uses_epics_write_pv_for_write_only_signal() -> None:
    signal = EpicsW(EpicsWConfig(write_pvname="PV:SP"))

    assert signal.measure_name() == "PV:SP"


def test_get_range_returns_configured_range_for_writable_signal() -> None:
    signal = EpicsW(EpicsWConfig(write_pvname="PV:SP", range=[0.0, 10.0]))
    signal._writable = True

    assert signal.get_range() == [0.0, 10.0]


def test_get_range_returns_configured_range_from_write_config() -> None:
    signal = EpicsW(EpicsWConfig(write_pvname="PV:SP", range=[0.0, 10.0]))
    signal._writable = False

    assert signal.get_range() == [0.0, 10.0]


def test_base_epics_write_config_has_default_unit_field() -> None:
    cfg = EpicsConfigW(write_pvname="PV:SP")

    assert cfg.unit == ""

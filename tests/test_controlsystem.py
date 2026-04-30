from __future__ import annotations

import pytest
from pyaml.common.exception import PyAMLException

from pyaml_cs_oa.controlsystem import ConfigModel, OphydAsyncControlSystem
from pyaml_cs_oa.epicsR import ConfigModel as EpicsRConfig
from pyaml_cs_oa.epicsR import EpicsR
from pyaml_cs_oa.epicsRW import ConfigModel as EpicsRWConfig
from pyaml_cs_oa.epicsW import ConfigModel as EpicsWConfig
from pyaml_cs_oa.tangoR import ConfigModel as TangoRConfig
from pyaml_cs_oa.tangoRW import ConfigModel as TangoRWConfig


def _no_connect_build(self) -> None:
    self.SP = None
    self.RB = None
    self._readable = True
    self._writable = False


def test_controlsystem_exposes_name_and_aggregator_modules() -> None:
    cfg = ConfigModel(name="live", prefix="PREFIX:", vector_aggregator="vector.mod")
    control_system = OphydAsyncControlSystem(cfg)

    assert control_system.name() == "live"
    assert control_system.scalar_aggregator() == "pyaml_cs_oa.scalar_aggregator"
    assert control_system.vector_aggregator() == "vector.mod"


def test_attach_prefixes_epics_read_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(EpicsR, "build", _no_connect_build)
    control_system = OphydAsyncControlSystem(ConfigModel(name="live", prefix="P:"))
    device = EpicsR(EpicsRConfig(read_pvname="RB"))

    attached = control_system.attach([device])[0]

    assert isinstance(attached, EpicsR)
    assert attached._cfg.read_pvname == "P:RB"


def test_attach_prefixes_epics_read_write_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pyaml_cs_oa.epicsRW.EpicsRW.build", _no_connect_build)
    control_system = OphydAsyncControlSystem(ConfigModel(name="live", prefix="P:"))
    device = EpicsR(EpicsRWConfig(read_pvname="RB", write_pvname="SP"))

    attached = control_system.attach([device])[0]

    assert attached._cfg.read_pvname == "P:RB"
    assert attached._cfg.write_pvname == "P:SP"


def test_attach_prefixes_epics_write_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pyaml_cs_oa.epicsW.EpicsW.build", _no_connect_build)
    control_system = OphydAsyncControlSystem(ConfigModel(name="live", prefix="P:"))
    device = EpicsR(EpicsWConfig(write_pvname="SP"))

    attached = control_system.attach([device])[0]

    assert attached._cfg.write_pvname == "P:SP"


def test_attach_prefixes_tango_devices(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pyaml_cs_oa.tangoR.TangoR.build", _no_connect_build)
    monkeypatch.setattr("pyaml_cs_oa.tangoRW.TangoRW.build", _no_connect_build)
    control_system = OphydAsyncControlSystem(
        ConfigModel(name="live", prefix="//tango-host:10000/"),
    )

    read_only, read_write = control_system.attach(
        [
            EpicsR(TangoRConfig(attribute="sys/tg_test/1/value")),
            EpicsR(TangoRWConfig(attribute="sys/tg_test/2/value")),
        ],
    )

    assert read_only._cfg.attribute == "//tango-host:10000/sys/tg_test/1/value"
    assert read_write._cfg.attribute == "//tango-host:10000/sys/tg_test/2/value"


def test_attach_reuses_existing_device_for_same_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(EpicsR, "build", _no_connect_build)
    control_system = OphydAsyncControlSystem(ConfigModel(name="live", prefix="P:"))

    first = control_system.attach([EpicsR(EpicsRConfig(read_pvname="RB"))])[0]
    second = control_system.attach([EpicsR(EpicsRConfig(read_pvname="RB"))])[0]

    assert first is second


def test_attach_preserves_none_entries() -> None:
    control_system = OphydAsyncControlSystem(ConfigModel(name="live"))

    assert control_system.attach([None]) == [None]


def test_attach_rejects_unsupported_config_type() -> None:
    class UnsupportedDevice:
        _cfg = object()

    control_system = OphydAsyncControlSystem(ConfigModel(name="live"))

    with pytest.raises(PyAMLException, match="Unsupported type"):
        control_system.attach([UnsupportedDevice()])

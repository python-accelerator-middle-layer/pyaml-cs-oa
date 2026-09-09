import pytest
from pyaml.common.exception import PyAMLException

from pyaml_cs_oa.dynamic_catalog import DynamicCatalog
from pyaml_cs_oa.types import EpicsConfigR, EpicsConfigRW, TangoConfigAtt


def test_dynamic_epics_catalog_resolves_scalar_read_key_without_index() -> None:
    catalog = DynamicCatalog(backend="epics", timeout_ms=1234)

    device = catalog.resolve("PV:RB[m]")

    assert isinstance(device, EpicsConfigR)
    assert device.read_pvname == "PV:RB"
    assert device.timeout_ms == 1234
    assert device.unit == "m"
    assert device.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_key() -> None:
    catalog = DynamicCatalog(backend="epics")

    device = catalog.resolve("PV:ARRAY@3[m]")

    assert isinstance(device, EpicsConfigR)
    assert device.read_pvname == "PV:ARRAY"
    assert device.unit == "m"
    assert device.index == 3


def test_dynamic_epics_catalog_resolves_read_write_key() -> None:
    catalog = DynamicCatalog(backend="epics")

    device = catalog.resolve("(PV:RB, PV:SP)[m]")

    assert isinstance(device, EpicsConfigRW)
    assert device.read_pvname == "PV:RB"
    assert device.write_pvname == "PV:SP"
    assert device.unit == "m"
    assert device.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_write_key() -> None:
    catalog = DynamicCatalog(backend="epics")

    device = catalog.resolve("(PV:RB, PV:SP)@5[m]")

    assert isinstance(device, EpicsConfigRW)
    assert device.read_pvname == "PV:RB"
    assert device.write_pvname == "PV:SP"
    assert device.unit == "m"
    assert device.index == 5


def test_dynamic_epics_catalog_strips_whitespace_from_pv_names_and_index() -> None:
    catalog = DynamicCatalog(backend="epics")

    device = catalog.resolve(" ( PV:RB , PV:SP ) @ 7 [m]")

    assert isinstance(device, EpicsConfigRW)
    assert device.read_pvname == "PV:RB"
    assert device.write_pvname == "PV:SP"
    assert device.index == 7
    assert device.unit == "m"


def test_dynamic_epics_catalog_rejects_invalid_index() -> None:
    catalog = DynamicCatalog(backend="epics")

    with pytest.raises(PyAMLException, match="Invalid index"):
        catalog.resolve("PV:ARRAY@not-an-index[m]")


def test_dynamic_epics_catalog_rejects_too_many_read_write_tokens() -> None:
    catalog = DynamicCatalog(backend="epics")

    with pytest.raises(PyAMLException, match="Too many comma-separated tokens"):
        catalog.resolve("(PV:ONE, PV:TWO, PV:THREE)[m]")


def test_tango_catalog_resolves_scalar_attribute() -> None:
    catalog = DynamicCatalog(backend="tango", timeout_ms=1234)

    device = catalog.resolve("sys/tg_test/1/value[m]")

    assert isinstance(device, TangoConfigAtt)
    assert device.attribute == "sys/tg_test/1/value"
    assert device.timeout_ms == 1234
    assert device.unit == "m"
    assert device.index is None


def test_disconnected_tango_catalog_resolves_indexed_attribute() -> None:
    catalog = DynamicCatalog(backend="tango")

    device = catalog.resolve("sys/tg_test/1/spectrum@4[m]")

    assert isinstance(device, TangoConfigAtt)
    assert device.attribute == "sys/tg_test/1/spectrum"
    assert device.index == 4


def test_tango_catalog_rejects_invalid_index() -> None:
    catalog = DynamicCatalog(backend="tango")

    with pytest.raises(PyAMLException, match="Invalid index"):
        catalog.resolve("sys/tg_test/1/spectrum@bad[m]")

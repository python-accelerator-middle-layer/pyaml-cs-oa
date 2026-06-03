import pytest
from pyaml.common.exception import PyAMLException

from pyaml_cs_oa.dynamic_catalog import ConfigModel as DynamicCatalogConfig
from pyaml_cs_oa.dynamic_catalog import DynamicCatalog
from pyaml_cs_oa.epicsR import ConfigModel as EpicsRConfig
from pyaml_cs_oa.epicsRW import ConfigModel as EpicsRWConfig
from pyaml_cs_oa.tangoAtt import ConfigModel as TangoAttConfig


def test_dynamic_epics_catalog_resolves_scalar_read_key_without_index() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics", timeout_ms=1234))

    device = catalog.resolve("PV:RB[m]")

    assert isinstance(device, EpicsRConfig)
    assert device.read_pvname == "PV:RB"
    assert device.timeout_ms == 1234
    assert device.unit == "m"
    assert device.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_key() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics"))

    device = catalog.resolve("PV:ARRAY@3[m]")

    assert isinstance(device, EpicsRConfig)
    assert device.read_pvname == "PV:ARRAY"
    assert device.unit == "m"
    assert device.index == 3


def test_dynamic_epics_catalog_resolves_read_write_key() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics"))

    device = catalog.resolve("(PV:RB, PV:SP)[m]")

    assert isinstance(device, EpicsRWConfig)
    assert device.read_pvname == "PV:RB"
    assert device.write_pvname == "PV:SP"
    assert device.unit == "m"
    assert device.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_write_key() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics"))

    device = catalog.resolve("(PV:RB, PV:SP)@5[m]")

    assert isinstance(device, EpicsRWConfig)
    assert device.read_pvname == "PV:RB"
    assert device.write_pvname == "PV:SP"
    assert device.unit == "m"
    assert device.index == 5


def test_dynamic_epics_catalog_strips_whitespace_from_pv_names_and_index() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics"))

    device = catalog.resolve(" ( PV:RB , PV:SP ) @ 7 [m]")

    assert isinstance(device, EpicsRWConfig)
    assert device.read_pvname == "PV:RB"
    assert device.write_pvname == "PV:SP"
    assert device.index == 7
    assert device.unit == "m"


def test_dynamic_epics_catalog_rejects_invalid_index() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics"))

    with pytest.raises(PyAMLException, match="Invalid index"):
        catalog.resolve("PV:ARRAY@not-an-index[m]")


def test_dynamic_epics_catalog_rejects_too_many_read_write_tokens() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="epics"))

    with pytest.raises(PyAMLException, match="Too many comma-separated tokens"):
        catalog.resolve("(PV:ONE, PV:TWO, PV:THREE)[m]")


def test_tango_catalog_resolves_scalar_attribute() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="tango", timeout_ms=1234))

    device = catalog.resolve("sys/tg_test/1/value[m]")

    assert isinstance(device, TangoAttConfig)
    assert device.attribute == "sys/tg_test/1/value"
    assert device.timeout_ms == 1234
    assert device.unit == "m"
    assert device.index is None


def test_disconnected_tango_catalog_resolves_indexed_attribute() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="tango"))

    device = catalog.resolve("sys/tg_test/1/spectrum@4[m]")

    assert isinstance(device, TangoAttConfig)
    assert device.attribute == "sys/tg_test/1/spectrum"
    assert device.index == 4


def test_tango_catalog_rejects_invalid_index() -> None:
    catalog = DynamicCatalog(DynamicCatalogConfig(backend="tango"))

    with pytest.raises(PyAMLException, match="Invalid index"):
        catalog.resolve("sys/tg_test/1/spectrum@bad[m]")


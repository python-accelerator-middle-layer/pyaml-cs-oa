import pytest
from pyaml.common.exception import PyAMLException

from pyaml_cs_oa.tango_catalog import ConfigModel, TangoCatalog
from pyaml_cs_oa.tangoR import TangoR
from pyaml_cs_oa.tangoRW import TangoRW


def test_disconnected_tango_catalog_resolves_scalar_attribute_as_read_write() -> None:
    catalog = TangoCatalog(ConfigModel(name="tango", disconnected=True, timeout_ms=1234))

    device = catalog.resolve("sys/tg_test/1/value")

    assert isinstance(device, TangoRW)
    assert device._cfg.attribute == "sys/tg_test/1/value"
    assert device._cfg.timeout_ms == 1234
    assert device._cfg.index is None


def test_disconnected_tango_catalog_resolves_indexed_attribute_as_read_only() -> None:
    catalog = TangoCatalog(ConfigModel(name="tango", disconnected=True))

    device = catalog.resolve("sys/tg_test/1/spectrum@4")

    assert isinstance(device, TangoR)
    assert device._cfg.attribute == "sys/tg_test/1/spectrum"
    assert device._cfg.index == 4
    assert device.is_array is True


def test_tango_catalog_reuses_resolved_device() -> None:
    catalog = TangoCatalog(ConfigModel(name="tango", disconnected=True))

    first = catalog.resolve("sys/tg_test/1/value")
    second = catalog.resolve("sys/tg_test/1/value")

    assert first is second


def test_tango_catalog_rejects_invalid_attribute_key() -> None:
    catalog = TangoCatalog(ConfigModel(name="tango", disconnected=True))

    with pytest.raises(PyAMLException, match="Expected 'domain/family/member/attribute"):
        catalog.resolve("sys/tg_test/value")


def test_tango_catalog_rejects_invalid_index() -> None:
    catalog = TangoCatalog(ConfigModel(name="tango", disconnected=True))

    with pytest.raises(PyAMLException, match="invalid index"):
        catalog.resolve("sys/tg_test/1/spectrum@bad")

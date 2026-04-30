from __future__ import annotations

import pytest

from pyaml_cs_oa.epics_catalog import ConfigModel, EpicsCatalog
from pyaml_cs_oa.epicsR import EpicsR
from pyaml_cs_oa.epicsRW import EpicsRW


def test_dynamic_epics_catalog_resolves_scalar_read_key_without_index() -> None:
    catalog = EpicsCatalog(ConfigModel(name="epics"))

    device = catalog.resolve("PV:RB")

    assert isinstance(device, EpicsR)
    assert device._cfg.read_pvname == "PV:RB"
    assert device._cfg.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_key() -> None:
    catalog = EpicsCatalog(ConfigModel(name="epics"))

    device = catalog.resolve("PV:ARRAY@3")

    assert isinstance(device, EpicsR)
    assert device._cfg.read_pvname == "PV:ARRAY"
    assert device._cfg.index == 3


def test_dynamic_epics_catalog_resolves_read_write_key() -> None:
    catalog = EpicsCatalog(ConfigModel(name="epics"))

    device = catalog.resolve("(PV:RB, PV:SP)")

    assert isinstance(device, EpicsRW)
    assert device._cfg.read_pvname == "PV:RB"
    assert device._cfg.write_pvname == "PV:SP"
    assert device._cfg.index is None


def test_dynamic_epics_catalog_rejects_invalid_index() -> None:
    catalog = EpicsCatalog(ConfigModel(name="epics"))

    with pytest.raises(Exception, match="invalid index"):
        catalog.resolve("PV:ARRAY@not-an-index")

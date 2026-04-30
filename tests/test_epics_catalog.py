import pytest
from pyaml.common.exception import PyAMLException

from pyaml_cs_oa.epics_catalog import ConfigModel as DynamicCatalogConfig
from pyaml_cs_oa.epics_catalog import EpicsCatalog
from pyaml_cs_oa.epics_static_catalog import ConfigModel as StaticCatalogConfig
from pyaml_cs_oa.epics_static_catalog import EpicsStaticCatalog
from pyaml_cs_oa.epics_static_catalog_entry import ConfigModel as StaticCatalogEntryConfig
from pyaml_cs_oa.epics_static_catalog_entry import EpicsStaticCatalogEntry
from pyaml_cs_oa.epicsR import ConfigModel as EpicsRConfig
from pyaml_cs_oa.epicsR import EpicsR
from pyaml_cs_oa.epicsRW import ConfigModel as EpicsRWConfig
from pyaml_cs_oa.epicsRW import EpicsRW
from pyaml_cs_oa.epicsW import ConfigModel as EpicsWConfig
from pyaml_cs_oa.epicsW import EpicsW


def _entry(key: str, device) -> EpicsStaticCatalogEntry:
    return EpicsStaticCatalogEntry(StaticCatalogEntryConfig(key=key, device=device))


def _record_build(self) -> None:
    self.build_calls = getattr(self, "build_calls", 0) + 1


def test_dynamic_epics_catalog_resolves_scalar_read_key_without_index() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics", timeout_ms=1234))

    device = catalog.resolve("PV:RB")

    assert isinstance(device, EpicsR)
    assert device._cfg.read_pvname == "PV:RB"
    assert device._cfg.timeout_ms == 1234
    assert device._cfg.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_key() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics"))

    device = catalog.resolve("PV:ARRAY@3")

    assert isinstance(device, EpicsR)
    assert device._cfg.read_pvname == "PV:ARRAY"
    assert device._cfg.index == 3


def test_dynamic_epics_catalog_resolves_read_write_key() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics"))

    device = catalog.resolve("(PV:RB, PV:SP)")

    assert isinstance(device, EpicsRW)
    assert device._cfg.read_pvname == "PV:RB"
    assert device._cfg.write_pvname == "PV:SP"
    assert device._cfg.index is None


def test_dynamic_epics_catalog_resolves_indexed_read_write_key() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics"))

    device = catalog.resolve("(PV:RB, PV:SP)@5")

    assert isinstance(device, EpicsRW)
    assert device._cfg.read_pvname == "PV:RB"
    assert device._cfg.write_pvname == "PV:SP"
    assert device._cfg.index == 5


def test_dynamic_epics_catalog_strips_whitespace_from_pv_names_and_index() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics"))

    device = catalog.resolve(" ( PV:RB , PV:SP ) @ 7 ")

    assert isinstance(device, EpicsRW)
    assert device._cfg.read_pvname == "PV:RB"
    assert device._cfg.write_pvname == "PV:SP"
    assert device._cfg.index == 7


def test_dynamic_epics_catalog_rejects_invalid_index() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics"))

    with pytest.raises(PyAMLException, match="invalid index"):
        catalog.resolve("PV:ARRAY@not-an-index")


def test_dynamic_epics_catalog_rejects_too_many_read_write_tokens() -> None:
    catalog = EpicsCatalog(DynamicCatalogConfig(name="epics"))

    with pytest.raises(PyAMLException, match="too many comma-separated tokens"):
        catalog.resolve("(PV:ONE, PV:TWO, PV:THREE)")


def test_static_epics_catalog_entry_exposes_key_and_device() -> None:
    device = EpicsR(EpicsRConfig(read_pvname="PV:RB"))
    entry = _entry("readback", device)

    assert entry.get_key() == "readback"
    assert entry.get_device() is device


def test_static_epics_catalog_resolves_read_write_and_write_entries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(EpicsR, "build", _record_build)
    monkeypatch.setattr(EpicsRW, "build", _record_build)
    monkeypatch.setattr(EpicsW, "build", _record_build)

    read = EpicsR(EpicsRConfig(read_pvname="PV:RB", index=2))
    read_write = EpicsRW(EpicsRWConfig(read_pvname="PV:RW:RB", write_pvname="PV:RW:SP"))
    write = EpicsW(EpicsWConfig(write_pvname="PV:SP"))
    catalog = EpicsStaticCatalog(
        StaticCatalogConfig(
            name="static-epics",
            entries=[
                _entry("read", read),
                _entry("read_write", read_write),
                _entry("write", write),
            ],
        ),
    )

    assert catalog.resolve("read") is read
    assert catalog.resolve("read_write") is read_write
    assert catalog.resolve("write") is write
    assert read.build_calls == 1
    assert read_write.build_calls == 1
    assert write.build_calls == 1


def test_static_epics_catalog_rejects_empty_entries() -> None:
    with pytest.raises(PyAMLException, match="must contain at least one entry"):
        EpicsStaticCatalog(StaticCatalogConfig(name="static-epics", entries=[]))


def test_static_epics_catalog_rejects_duplicate_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(EpicsR, "build", _record_build)
    first = EpicsR(EpicsRConfig(read_pvname="PV:FIRST"))
    second = EpicsR(EpicsRConfig(read_pvname="PV:SECOND"))

    with pytest.raises(PyAMLException, match="duplicate key 'read'"):
        EpicsStaticCatalog(
            StaticCatalogConfig(
                name="static-epics",
                entries=[
                    _entry("read", first),
                    _entry("read", second),
                ],
            ),
        )


def test_static_epics_catalog_rejects_unknown_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(EpicsR, "build", _record_build)
    catalog = EpicsStaticCatalog(
        StaticCatalogConfig(
            name="static-epics",
            entries=[_entry("read", EpicsR(EpicsRConfig(read_pvname="PV:RB")))],
        ),
    )

    with pytest.raises(PyAMLException, match="cannot resolve key 'missing'"):
        catalog.resolve("missing")

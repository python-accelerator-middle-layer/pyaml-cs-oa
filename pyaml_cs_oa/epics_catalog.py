from pydantic import ConfigDict

from pyaml.common.exception import PyAMLException
from pyaml.configuration.catalog import Catalog, CatalogConfigModel
from pyaml.control.deviceaccess import DeviceAccess

PYAMLCLASS = "EpicsCatalog"


class ConfigModel(CatalogConfigModel):
    """
    Dynamic EPICS catalog.

    The key passed to ``resolve()`` IS the PV specification string — no
    ``entries`` list required.  Resolutions are cached after the first call.

    Supported key formats::

        "PV"                → scalar read-only
        "PV@n"              → array PV, element n, read-only
        "R_PV, W_PV"        → scalar read-write
        "R_PV@n, W_PV@m"    → indexed read + indexed write (read-modify-write)
        "R:PV@n, W:PV@m"    → same (colons are part of the PV name)
        "R_PV@n, W_PV"      → indexed read + scalar write
        "R_PV, W_PV@m"      → scalar read + indexed write

    The ``prefix`` is prepended to every PV name extracted from the key.

    Example
    -------
    .. code-block:: yaml

        type: pyaml_cs_oa.epics_catalog
        name: id-catalog
        prefix: ""
        timeout_ms: 3000
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    prefix: str = ""
    timeout_ms: int = 3000


class EpicsCatalog(Catalog):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)
        self._refs: dict[str, DeviceAccess] = {}

    def resolve(self, key: str) -> DeviceAccess:
        if key not in self._refs:
            try:
                self._refs[key] = _build_device(key, self._cfg.prefix, self._cfg.timeout_ms)
            except PyAMLException:
                raise
            except Exception as exc:
                raise PyAMLException(
                    f"EpicsCatalog '{self.get_name()}' cannot resolve key '{key}': {exc}"
                ) from exc
        return self._refs[key]


# ── PV spec parser ────────────────────────────────────────────────────────────

def _parse_pv(token: str) -> tuple[str, int | None]:
    """Split ``'PV_NAME[@index]'`` into ``(pv_name, index_or_None)``."""
    token = token.strip()
    if "@" in token:
        pv_name, idx_str = token.rsplit("@", 1)
        try:
            return pv_name.strip(), int(idx_str.strip())
        except ValueError:
            raise PyAMLException(f"EpicsCatalog: invalid index in PV token '{token}'")
    return token, None


def _build_device(pv_str: str, prefix: str, timeout_ms: int) -> DeviceAccess:
    tokens = [t.strip() for t in pv_str.split(",")]
    if len(tokens) == 1:
        return _build_single(tokens[0], prefix, timeout_ms)
    if len(tokens) == 2:
        return _build_pair(tokens[0], tokens[1], prefix, timeout_ms)
    raise PyAMLException(
        f"EpicsCatalog: too many comma-separated tokens in key '{pv_str}' (max 2)"
    )


def _build_single(token: str, prefix: str, timeout_ms: int) -> DeviceAccess:
    from .epicsR import EpicsR, ConfigModel as EpicsRConfig

    pv_name, index = _parse_pv(token)
    sig = EpicsR(EpicsRConfig(read_pvname=prefix + pv_name, timeout_ms=timeout_ms, index=index))
    sig.build()
    return sig


def _build_pair(read_token: str, write_token: str, prefix: str, timeout_ms: int) -> DeviceAccess:
    read_pv, read_idx = _parse_pv(read_token)
    write_pv, write_idx = _parse_pv(write_token)
    full_read = prefix + read_pv
    full_write = prefix + write_pv

    if read_idx is None and write_idx is None:
        from .epicsRW import EpicsRW, ConfigModel as EpicsRWConfig
        sig = EpicsRW(EpicsRWConfig(read_pvname=full_read, write_pvname=full_write,
                                    timeout_ms=timeout_ms))
        sig.build()
        return sig

    if read_idx is not None and write_idx is not None:
        # Both indexed (same or different): EpicsRW carries both indexes.
        from .epicsRW import EpicsRW, ConfigModel as EpicsRWConfig
        sig = EpicsRW(EpicsRWConfig(read_pvname=full_read, write_pvname=full_write,
                                    timeout_ms=timeout_ms,
                                    read_index=read_idx, write_index=write_idx))
        sig.build()
        return sig

    # Mixed (one side array, one side scalar): build independently and combine.
    from .epicsR import EpicsR, ConfigModel as EpicsRConfig
    from .epicsW import EpicsW, ConfigModel as EpicsWConfig
    from .indexed_signal import IndexedFloatSignal

    r_sig = EpicsR(EpicsRConfig(read_pvname=full_read, timeout_ms=timeout_ms, index=read_idx))
    r_sig.build()
    w_sig = EpicsW(EpicsWConfig(write_pvname=full_write, timeout_ms=timeout_ms, index=write_idx))
    w_sig.build()

    measure = f"{read_pv}[{read_idx}]" if read_idx is not None else read_pv
    return IndexedFloatSignal(r_sig.RB, w_sig.SP, measure_name=measure)

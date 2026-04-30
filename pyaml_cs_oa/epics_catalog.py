from pyaml.common.exception import PyAMLException
from pyaml.configuration.catalog import Catalog, CatalogConfigModel
from pyaml.control.deviceaccess import DeviceAccess
from pydantic import ConfigDict

PYAMLCLASS = "EpicsCatalog"


class ConfigModel(CatalogConfigModel):
    """
    Dynamic EPICS catalog.

    The key passed to ``resolve()`` IS the PV specification string — no
    ``entries`` list required.  Resolutions are cached after the first call.

    Supported key formats::
    (TODO write only)

        "PV"                → scalar read-only
        "PV@n"              → array PV, element n, read-only
        "(R_PV, W_PV)"      → scalar read-write
        "(R_PV, W_PV)@n"    → scalar indexed read-write

    Example
    -------
    .. code-block:: yaml

        type: pyaml_cs_oa.epics_catalog
        name: id-catalog
        timeout_ms: 3000
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    timeout_ms: int = 3000
    prefix: str = ""  # Ignored


class EpicsCatalog(Catalog):
    def __init__(self, cfg: ConfigModel):
        super().__init__(cfg)

    def resolve(self, key: str) -> DeviceAccess:
        return _build_device(key, self._cfg.timeout_ms)


# ── PV spec parser ────────────────────────────────────────────────────────────


def _parse_pv(token: str) -> tuple[list[str], int | None]:
    token = token.strip()

    # No suffix means scalar access to the full PV value.
    index = None
    if "@" in token:
        token, idx_str = token.rsplit("@", 1)
        token = token.strip()
        try:
            index = int(idx_str.strip())
        except ValueError:
            raise PyAMLException(f"EpicsCatalog: invalid index in PV token '{token}'") from None

    # Parenthesized keys describe one read PV and one write PV.
    if token.startswith("(") and token.endswith(")"):
        names = token[1:-1]
        name_list = [name.strip() for name in names.split(",")]
    else:
        name_list = [token.strip()]

    return name_list, index


def _build_device(pv_str: str, timeout_ms: int) -> DeviceAccess:
    from .epicsR import ConfigModel as EpicsRConfig
    from .epicsR import EpicsR
    from .epicsRW import ConfigModel as EpicsRWConfig
    from .epicsRW import EpicsRW

    pv_names, index = _parse_pv(pv_str)
    if len(pv_names) == 1:
        return EpicsR(EpicsRConfig(read_pvname=pv_names[0], timeout_ms=timeout_ms, index=index))
    if len(pv_names) == 2:
        return EpicsRW(EpicsRWConfig(read_pvname=pv_names[0], write_pvname=pv_names[1], timeout_ms=timeout_ms, index=index))
    raise PyAMLException(f"EpicsCatalog: too many comma-separated tokens in key '{pv_str}' (max 2)")

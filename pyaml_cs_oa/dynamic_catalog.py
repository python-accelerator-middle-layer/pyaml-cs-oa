from typing import Tuple

from pyaml.common.exception import PyAMLException
from pyaml.control.deviceaccess import DeviceAccess
from pydantic import BaseModel, ConfigDict

from .catalog import Catalog

PYAMLCLASS = "DynamicCatalog"


class ConfigModel(BaseModel):
    """
    Default dynamic catalog.

    The key passed to ``resolve()`` is the PV or Tango attribute specification string — no
    ``entries`` list required.  Resolutions are cached after the first call.

    Supported key formats::

    For EPCIS::

    - ``READ_PV[unit]``                   → scalar read-only
    - ``(WRITE_PV)[unit]``                → scalar write-only
    - ``READ_PV@index[unit]``             → array PV with element index, read-only
    - ``(READ_PV, WRITE_PV)[unit]``       → scalar read-write
    - ``(READ_PV, WRITE_PV)@index[unit]`` → array PV with element index read-write

    For Tango::

    - ``domain/family/member/attribute[unit]``       → scalar signal
    - ``domain/family/member/attribute@index[unit]`` → one element of a SPECTRUM signal

    Example
    -------
    .. code-block:: yaml
        backend: "Tango" or "Epics"
        timeout_ms: 3000
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    timeout_ms: int = 3000
    backend: str = ""


class DynamicCatalog(Catalog):
    def __init__(self, cfg: ConfigModel):
        self._cfg = cfg
        self._dp = {}  # Device proxy cache (Tango Only)
        if cfg.backend.lower() != "tango" and cfg.backend.lower() != "epics":
            raise PyAMLException(f"backend must be `epics` or `tango` but got '{cfg.backend}'") from None

    def resolve(self, key: str) -> BaseModel:
        if self._cfg.backend.lower() == "epics":
            return _build_epics_config(key, self._cfg.timeout_ms)
        elif self._cfg.backend.lower() == "tango":
            return _build_tango_config(key, self._cfg.timeout_ms)
        else:
            return None


def _extract_unit(token: str) -> Tuple[str, str]:
    # Extract unit block
    try:
        start_idx = token.index("[") + 1
        end_idx = token.index("]", start_idx)
        return (token[start_idx:end_idx], token[: start_idx - 1])
    except ValueError:
        return "", token  # No unit


# ── PV spec parser ────────────────────────────────────────────────────────────


def _parse_pv(token: str) -> tuple[list[str], int | None, str, bool]:
    token = token.strip()

    unit, token = _extract_unit(token)

    # No suffix means scalar access to the full PV value.
    index = None
    if "@" in token:
        token, idx_str = token.rsplit("@", 1)
        token = token.strip()
        try:
            index = int(idx_str.strip())
        except ValueError:
            raise PyAMLException(f"Invalid index for {token}, cannot parse '{idx_str}' as number") from None

    # Parenthesized keys describe one read PV and one write PV.
    if token.startswith("(") and token.endswith(")"):
        hasw = True
        names = token[1:-1]
        name_list = [name.strip() for name in names.split(",")]
    else:
        hasw = False
        name_list = [token.strip()]

    return name_list, index, unit, hasw


def _build_epics_config(pv_str: str, timeout_ms: int) -> DeviceAccess:
    from .epicsR import ConfigModel as EpicsRConfig
    from .epicsRW import ConfigModel as EpicsRWConfig
    from .epicsW import ConfigModel as EpicsWConfig

    pv_names, index, unit, hasw = _parse_pv(pv_str)
    if len(pv_names) == 1:
        if hasw:
            return EpicsWConfig(write_pvname=pv_names[0], timeout_ms=timeout_ms, index=index, unit=unit)
        else:
            return EpicsRConfig(read_pvname=pv_names[0], timeout_ms=timeout_ms, index=index, unit=unit)
    if len(pv_names) == 2:
        return EpicsRWConfig(read_pvname=pv_names[0], write_pvname=pv_names[1], timeout_ms=timeout_ms, index=index, unit=unit)
    raise PyAMLException(f"Too many comma-separated tokens in key '{pv_str}' (max 2)")


# ── Tango spec parser ────────────────────────────────────────────────────────────


def _parse_attribute(token: str) -> tuple[list[str], int | None, str]:
    token = token.strip()

    unit, token = _extract_unit(token)

    # No suffix means scalar access to the full PV value.
    index = None
    if "@" in token:
        token, idx_str = token.rsplit("@", 1)
        token = token.strip()
        try:
            index = int(idx_str.strip())
        except ValueError:
            raise PyAMLException(f"Invalid index for {token}, cannot parse '{idx_str}' as number") from None

    return token, index, unit


def _build_tango_config(att_name: str, timeout_ms: int) -> BaseModel:
    from .tangoAtt import ConfigModel as TangoAtt

    att_name, index, unit = _parse_attribute(att_name)
    return TangoAtt(attribute=att_name, timeout_ms=timeout_ms, index=index, unit=unit)

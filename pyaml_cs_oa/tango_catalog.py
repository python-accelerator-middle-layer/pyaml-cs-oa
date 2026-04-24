from pydantic import ConfigDict

import pyaml
from pyaml.common.exception import PyAMLException
from pyaml.configuration.catalog import Catalog, CatalogConfigModel, CatalogResolver
from pyaml.control.deviceaccess import DeviceAccess

PYAMLCLASS = "TangoCatalog"


class ConfigModel(CatalogConfigModel):
    """
    Dynamic Tango catalog resolving keys that are Tango attribute references.

    Supported key formats:
    - ``domain/family/member/attribute``          → scalar signal
    - ``domain/family/member/attribute@index``    → one element of a SPECTRUM signal

    In *disconnected* mode (``disconnected: true``) the catalog builds signals
    without querying Tango (writability and data-format are not verified).
    In *connected* mode the catalog queries ``tango.AttributeProxy`` at first
    resolution to detect writability and, for indexed keys, to verify SPECTRUM.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    disconnected: bool = False
    timeout_ms: int = 3000


class TangoCatalog(Catalog):
    def resolve(self, key: str) -> DeviceAccess:
        raise PyAMLException(
            f"OA Tango catalog '{self.get_name()}' must be attached to a control "
            f"system before resolving key '{key}'"
        )

    def attach_control_system(self, control_system):
        from .controlsystem import OphydAsyncControlSystem

        if not isinstance(control_system, OphydAsyncControlSystem):
            raise PyAMLException(
                f"OA Tango catalog '{self.get_name()}' can only be attached to "
                "OphydAsyncControlSystem"
            )
        return _TangoCatalogResolver(self, control_system)


class _TangoCatalogResolver(CatalogResolver):
    _WRITABLE_TYPES: set  # populated lazily after tango is imported

    def __init__(self, catalog: TangoCatalog, control_system):
        self._catalog = catalog
        self._control_system = control_system
        self._refs: dict[str, DeviceAccess] = {}

    def resolve(self, key: str) -> DeviceAccess:
        if key not in self._refs:
            attr_path, index = self._parse_key(key)
            if index is not None:
                self._refs[key] = self._build_indexed(attr_path, index)
            else:
                self._refs[key] = self._build_attribute(attr_path)
        return self._refs[key]

    # ── key parsing ──────────────────────────────────────────────────────────

    def _parse_key(self, key: str) -> tuple[str, int | None]:
        if not isinstance(key, str):
            raise PyAMLException(
                f"OA Tango catalog '{self._catalog.get_name()}' expects string keys, "
                f"got {type(key).__name__}"
            )
        if "@" in key:
            attr_path, idx_str = key.rsplit("@", 1)
            try:
                index = int(idx_str)
            except ValueError:
                raise PyAMLException(
                    f"OA Tango catalog '{self._catalog.get_name()}': invalid index "
                    f"'{idx_str}' in key '{key}'"
                )
        else:
            attr_path = key
            index = None

        parts = attr_path.split("/")
        if len(parts) != 4 or any(p == "" for p in parts):
            raise PyAMLException(
                f"OA Tango catalog '{self._catalog.get_name()}' cannot resolve '{key}'. "
                "Expected 'domain/family/member/attribute[@index]'."
            )
        return attr_path, index

    # ── signal builders ──────────────────────────────────────────────────────

    def _timeout(self) -> int:
        return self._catalog._cfg.timeout_ms

    def _build_attribute(self, attr_path: str) -> DeviceAccess:
        if self._catalog._cfg.disconnected:
            return self._make_rw(attr_path, is_array=False)

        try:
            import tango
        except ImportError as exc:
            raise PyAMLException(
                "pytango is required for TangoCatalog in connected mode"
            ) from exc

        try:
            attr_cfg = tango.AttributeProxy(attr_path).get_config()
        except tango.DevFailed as df:
            raise PyAMLException(
                f"OA Tango catalog '{self._catalog.get_name()}' cannot resolve "
                f"'{attr_path}': {df}"
            ) from df

        writable_types = {
            tango.AttrWriteType.READ_WRITE,
            tango.AttrWriteType.WRITE,
            tango.AttrWriteType.READ_WITH_WRITE,
        }
        is_writable = (
            getattr(attr_cfg, "writable", tango.AttrWriteType.WT_UNKNOWN)
            in writable_types
        )
        is_array = (
            getattr(attr_cfg, "data_format", None) == tango.AttrDataFormat.SPECTRUM
        )

        if is_writable:
            return self._make_rw(attr_path, is_array=is_array)
        return self._make_r(attr_path, is_array=is_array)

    def _build_indexed(self, attr_path: str, index: int) -> DeviceAccess:
        if not self._catalog._cfg.disconnected:
            try:
                import tango
            except ImportError as exc:
                raise PyAMLException(
                    "pytango is required for TangoCatalog in connected mode"
                ) from exc

            try:
                attr_cfg = tango.AttributeProxy(attr_path).get_config()
            except tango.DevFailed as df:
                raise PyAMLException(
                    f"OA Tango catalog '{self._catalog.get_name()}' cannot resolve "
                    f"'{attr_path}@{index}': {df}"
                ) from df

            data_format = getattr(attr_cfg, "data_format", None)
            if data_format != tango.AttrDataFormat.SPECTRUM:
                raise PyAMLException(
                    f"OA Tango catalog '{self._catalog.get_name()}': '{attr_path}' "
                    "is not a SPECTRUM; indexed access requires a vector attribute."
                )

        # index is embedded in the config; build() applies it automatically.
        return self._make_r(attr_path, index=index)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _make_r(self, attr_path: str, is_array: bool = False, index: int | None = None):
        from .tangoR import TangoR, ConfigModel as TangoRConfig

        sig = TangoR(TangoRConfig(attribute=attr_path, timeout_ms=self._timeout(), index=index), is_array)
        sig.build()
        return sig

    def _make_rw(self, attr_path: str, is_array: bool = False):
        from .tangoRW import TangoRW, ConfigModel as TangoRWConfig

        sig = TangoRW(TangoRWConfig(attribute=attr_path, timeout_ms=self._timeout()), is_array)
        sig.build()
        return sig

"""
TOML serialization for TyConf (Python 3.13+).

Read support: Built-in via tomllib (Python 3.11+)
Write support: Requires tomli-w (optional dependency)
"""

import tomllib
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ..core import TyConf

try:
    import tomli_w  # type: ignore[import-not-found]

    HAS_TOML_WRITE = True
except ImportError:
    HAS_TOML_WRITE = False

type TomlDict = dict[str, Any]


class TOMLSerializer:
    """TOML serializer with read (built-in) and optional write support."""

    def serialize(self, config: "TyConf", /, *, values_only: bool = False) -> str:
        """
        Serialize TyConf to TOML string.

        Requires: pip install tyconf[toml]

        Args:
            config: TyConf instance
            values_only: Export only values

        Returns:
            TOML string

        Raises:
            ImportError: If tomli-w is not installed

        Examples:
            >>> serializer = TOMLSerializer()
            >>> toml_str = serializer.serialize(config, values_only=True)
        """
        if not HAS_TOML_WRITE:
            raise ImportError(
                "TOML writing requires 'tomli-w' package.\n"
                "Install with: pip install tyconf[toml]"
            )

        data = self._prepare_data(config, values_only=values_only)

        # Cast Any return from tomli_w to str to satisfy return type
        return cast(str, tomli_w.dumps(data))

    def deserialize(self, data: str | bytes, /) -> TomlDict:
        """
        Deserialize TOML string/bytes to dict.

        Built-in support (Python 3.11+), no dependencies needed.

        Args:
            data: TOML string or bytes

        Returns:
            Dictionary with configuration data

        Examples:
            >>> serializer = TOMLSerializer()
            >>> data = serializer.deserialize(toml_string)
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        return tomllib.loads(data.decode("utf-8"))

    def _prepare_data(self, config: "TyConf", /, *, values_only: bool = False) -> TomlDict:
        """
        Prepare configuration data for TOML serialization.

        Args:
            config: TyConf instance
            values_only: If True, export only values

        Returns:
            Dictionary ready for TOML serialization
        """
        if values_only:
            return dict(config._values)

        # Full metadata export
        from .. import __version__

        # Explicitly type 'result' to avoid inference issues (e.g., inferring as dict[str, object])
        result: TomlDict = {"_tyconf_version": __version__, "properties": {}}

        for name, prop in config._properties.items():
            prop_data = {
                "type": prop.prop_type.__name__,
                "value": config._values[name],
                "default": prop.default_value,
                "readonly": prop.readonly,
            }

            if prop.validator:
                prop_data["has_validator"] = True

            result["properties"][name] = prop_data

        return result

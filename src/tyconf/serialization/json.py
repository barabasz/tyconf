"""
JSON serialization for TyConf (Python 3.13+).

Provides JSON import/export with full metadata support.
"""

import json
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ..core import TyConf

type JsonDict = dict[str, Any]


class JSONSerializer:
    """JSON serializer for TyConf configurations."""

    def serialize(
        self,
        config: "TyConf",
        /,
        *,
        values_only: bool = False,
        indent: int | None = 2,
    ) -> str:
        """
        Serialize TyConf to JSON string.

        Args:
            config: TyConf instance (positional-only)
            values_only: Export only values without metadata (keyword-only)
            indent: JSON indentation (keyword-only)

        Returns:
            JSON string

        Examples:
            >>> serializer = JSONSerializer()
            >>> json_str = serializer.serialize(config, values_only=True)
        """
        data = self._prepare_data(config, values_only=values_only)
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def deserialize(self, data: str, /) -> JsonDict:
        """
        Deserialize JSON string to dict.

        Args:
            data: JSON string (positional-only)

        Returns:
            Dictionary with configuration data

        Examples:
            >>> serializer = JSONSerializer()
            >>> data = serializer.deserialize(json_string)
        """
        return cast(JsonDict, json.loads(data))

    def _prepare_data(self, config: "TyConf", /, *, values_only: bool = False) -> JsonDict:
        """
        Prepare configuration data for serialization.

        Args:
            config: TyConf instance
            values_only: If True, export only values

        Returns:
            Dictionary ready for JSON serialization
        """
        if values_only:
            return dict(config._values)

        # Full metadata export
        from .. import __version__

        properties = {}
        for name, prop in config._properties.items():
            prop_data = {
                "type": prop.prop_type.__name__,
                "value": config._values[name],
                "default": prop.default_value,
                "readonly": prop.readonly,
            }

            # Note: Validators are not serializable
            # Users must provide them when loading
            if prop.validator:
                prop_data["has_validator"] = True

            properties[name] = prop_data

        return {"_tyconf_version": __version__, "properties": properties}

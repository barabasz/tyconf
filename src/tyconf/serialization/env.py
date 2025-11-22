"""Environment variable loading for TyConf (Python 3.13+)."""

import os
from typing import Any

type Schema = dict[str, tuple]


class ENVLoader:
    """Load configuration from environment variables."""

    @staticmethod
    def load(prefix: str, /, *, schema: Schema) -> dict[str, Any]:
        """
        Load configuration from environment variables.

        Only returns properties that have corresponding environment variables.
        Properties without env vars are NOT included in result.

        Args:
            prefix: Environment variable prefix (e.g., 'APP_')
            schema: Property schema {name: (type, default)}

        Returns:
            Dictionary with loaded values (only for properties with env vars)

        Examples:
            >>> # Environment: APP_HOST=localhost, APP_PORT=8080
            >>> loader = ENVLoader()
            >>> data = loader.load('APP_', schema={
            ...     'host': (str, 'localhost'),
            ...     'port': (int, 8080),
            ...     'debug': (bool, False)  # No APP_DEBUG in env
            ... })
            >>> # Returns: {'host': 'localhost', 'port': 8080}
            >>> # Note: 'debug' is NOT in result (no env var)
        """
        result = {}

        for prop_name, (prop_type, default_value) in schema.items():
            # Construct environment variable name
            env_name = f"{prefix}{prop_name.upper()}"

            # Case-insensitive lookup
            env_value = None
            for key in os.environ:
                if key.upper() == env_name.upper():
                    env_value = os.environ[key]
                    break

            # ✅ ONLY add to result if env var exists
            if env_value is not None:
                result[prop_name] = ENVLoader._convert_type(env_value, prop_type, prop_name)
            # ✅ If no env var, DON'T add to result (don't use default)

        return result

    @staticmethod
    def _convert_type(value: str, target_type: type, prop_name: str) -> Any:
        """
        Convert string value to target type.

        Args:
            value: String value from environment
            target_type: Target type to convert to
            prop_name: Property name (for error messages)

        Returns:
            Converted value

        Raises:
            ValueError: If conversion fails
        """
        # Handle bool specially
        if target_type is bool:
            return value.lower() in ("true", "1", "yes", "on")

        # Handle None/Optional
        if value.lower() in ("none", "null", ""):
            return None

        # Try direct conversion
        try:
            return target_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert environment variable '{prop_name}' "
                f"value '{value}' to {target_type.__name__}: {e}"
            ) from e

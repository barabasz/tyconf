"""
TyConf - Built-in validators for value validation.

This module provides ready-to-use validators for common validation scenarios.
"""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Type alias for better readability and Mypy compliance
# A validator takes a value of Any type and returns a bool or raises ValueError
type Validator = Callable[[Any], bool]


# ============================================================================
# COMBINATOR VALIDATORS - Combine multiple validators
# ============================================================================


def all_of(*validators: Validator) -> Validator:
    """
    Combine multiple validators - all must pass.

    Args:
        *validators: Validator functions to combine.

    Returns:
        Combined validator function.
    """

    def validator(value: Any) -> bool:
        for v in validators:
            v(value)  # Will raise ValueError if fails
        return True

    return validator


def any_of(*validators: Validator) -> Validator:
    """
    Combine multiple validators - at least one must pass.

    Args:
        *validators: Validator functions to combine.

    Returns:
        Combined validator function.
    """

    def validator(value: Any) -> bool:
        errors = []
        for v in validators:
            try:
                v(value)
                return True  # At least one passed
            except ValueError as e:
                errors.append(str(e))

        # All failed
        raise ValueError(f"must satisfy at least one of: {'; '.join(errors)}")

    return validator


# ============================================================================
# CHOICE VALIDATORS - Validate against allowed/disallowed values
# ============================================================================


def one_of(*allowed_values: Any) -> Validator:
    """
    Validate that a value is one of the allowed values.

    Args:
        *allowed_values: Allowed values.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value not in allowed_values:
            raise ValueError(f"must be one of {allowed_values}")
        return True

    return validator


def not_in(*disallowed_values: Any) -> Validator:
    """
    Validate that a value is NOT in the disallowed set.

    Args:
        *disallowed_values: Disallowed values.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value in disallowed_values:
            raise ValueError(f"must not be one of {disallowed_values}")
        return True

    return validator


# ============================================================================
# STRING VALIDATORS - Length
# ============================================================================


def length(min_len: int | None = None, max_len: int | None = None) -> Validator:
    """
    Validate that a string or collection has length within the specified range.

    Args:
        min_len: Minimum allowed length (inclusive). None means no minimum.
        max_len: Maximum allowed length (inclusive). None means no maximum.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        actual_len = len(value)
        if min_len is not None and actual_len < min_len:
            raise ValueError(f"length must be >= {min_len}")
        if max_len is not None and actual_len > max_len:
            raise ValueError(f"length must be <= {max_len}")
        return True

    return validator


def min_length(min_len: int) -> Validator:
    """
    Validate that a string or collection has minimum length.

    Args:
        min_len: Minimum allowed length (inclusive).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if len(value) < min_len:
            raise ValueError(f"length must be >= {min_len}")
        return True

    return validator


def max_length(max_len: int) -> Validator:
    """
    Validate that a string or collection has maximum length.

    Args:
        max_len: Maximum allowed length (inclusive).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if len(value) > max_len:
            raise ValueError(f"length must be <= {max_len}")
        return True

    return validator


# ============================================================================
# STRING VALIDATORS - Content matching
# ============================================================================


def contains(substring: str, case_sensitive: bool = True) -> Validator:
    """
    Validate that a string contains a specific substring.

    Args:
        substring: The string that must be present.
        case_sensitive: Whether matching should be case-sensitive.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        # We assume value is str; if not, Python runtime will raise AttributeError
        val_to_check = value if case_sensitive else value.lower()
        sub_to_check = substring if case_sensitive else substring.lower()

        if sub_to_check not in val_to_check:
            msg = f"must contain '{substring}'"
            if not case_sensitive:
                msg += " (case insensitive)"
            raise ValueError(msg)
        return True

    return validator


def starts_with(prefix: str, case_sensitive: bool = True) -> Validator:
    """
    Validate that a string starts with the specified prefix.

    Args:
        prefix: Required prefix string.
        case_sensitive: Whether matching should be case-sensitive.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        val_to_check = value if case_sensitive else value.lower()
        prefix_to_check = prefix if case_sensitive else prefix.lower()

        if not val_to_check.startswith(prefix_to_check):
            msg = f"must start with '{prefix}'"
            if not case_sensitive:
                msg += " (case insensitive)"
            raise ValueError(msg)
        return True

    return validator


def ends_with(suffix: str, case_sensitive: bool = True) -> Validator:
    """
    Validate that a string ends with the specified suffix.

    Args:
        suffix: Required suffix string.
        case_sensitive: Whether matching should be case-sensitive.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        val_to_check = value if case_sensitive else value.lower()
        suffix_to_check = suffix if case_sensitive else suffix.lower()

        if not val_to_check.endswith(suffix_to_check):
            msg = f"must end with '{suffix}'"
            if not case_sensitive:
                msg += " (case insensitive)"
            raise ValueError(msg)
        return True

    return validator


def regex(pattern: str) -> Validator:
    """
    Validate that a string matches the specified regular expression pattern.

    Args:
        pattern: Regular expression pattern to match.

    Returns:
        Validator function.
    """
    compiled = re.compile(pattern)

    def validator(value: Any) -> bool:
        if not compiled.match(value):
            raise ValueError(f"must match pattern {pattern}")
        return True

    return validator


# ============================================================================
# STRING VALIDATORS - Character type
# ============================================================================


def is_alpha() -> Validator:
    """
    Validate that a string contains only alphabetic characters.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not value.isalpha():
            raise ValueError("must contain only alphabetic characters")
        return True

    return validator


def is_alphanumeric() -> Validator:
    """
    Validate that a string contains only alphanumeric characters.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not value.isalnum():
            raise ValueError("must contain only alphanumeric characters")
        return True

    return validator


def is_numeric() -> Validator:
    """
    Validate that a string contains only numeric characters.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not value.isdigit():
            raise ValueError("must contain only numeric characters")
        return True

    return validator


def is_lowercase() -> Validator:
    """
    Validate that a string contains only lowercase characters.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not value.islower():
            raise ValueError("must be lowercase")
        return True

    return validator


def is_uppercase() -> Validator:
    """
    Validate that a string contains only uppercase characters.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not value.isupper():
            raise ValueError("must be uppercase")
        return True

    return validator


def no_whitespace() -> Validator:
    """
    Validate that a string contains no whitespace characters.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if any(c.isspace() for c in value):
            raise ValueError("must not contain whitespace")
        return True

    return validator


# ============================================================================
# NUMERIC VALIDATORS - Range
# ============================================================================


def range(min_val: int | float | None = None, max_val: int | float | None = None) -> Validator:
    """
    Validate that a numeric value is within the specified range.

    Args:
        min_val: Minimum allowed value (inclusive).
        max_val: Maximum allowed value (inclusive).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if min_val is not None and value < min_val:
            raise ValueError(f"must be >= {min_val}")
        if max_val is not None and value > max_val:
            raise ValueError(f"must be <= {max_val}")
        return True

    return validator


def between(min_val: int | float, max_val: int | float, inclusive: bool = True) -> Validator:
    """
    Validate that a numeric value is between min and max.

    Args:
        min_val: Minimum value.
        max_val: Maximum value.
        inclusive: If True, includes boundaries.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if inclusive:
            if not (min_val <= value <= max_val):
                raise ValueError(f"must be between {min_val} and {max_val} (inclusive)")
        else:
            if not (min_val < value < max_val):
                raise ValueError(f"must be between {min_val} and {max_val} (exclusive)")
        return True

    return validator


# ============================================================================
# NUMERIC VALIDATORS - Sign
# ============================================================================


def positive() -> Validator:
    """
    Validate that a number is positive (> 0).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value <= 0:
            raise ValueError("must be positive (> 0)")
        return True

    return validator


def negative() -> Validator:
    """
    Validate that a number is negative (< 0).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value >= 0:
            raise ValueError("must be negative (< 0)")
        return True

    return validator


def non_negative() -> Validator:
    """
    Validate that a number is non-negative (>= 0).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value < 0:
            raise ValueError("must be non-negative (>= 0)")
        return True

    return validator


def non_positive() -> Validator:
    """
    Validate that a number is non-positive (<= 0).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value > 0:
            raise ValueError("must be non-positive (<= 0)")
        return True

    return validator


# ============================================================================
# NUMERIC VALIDATORS - Divisibility and parity
# ============================================================================


def divisible_by(divisor: int) -> Validator:
    """
    Validate that a number is divisible by the specified divisor.

    Args:
        divisor: The number that value must be divisible by.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value % divisor != 0:
            raise ValueError(f"must be divisible by {divisor}")
        return True

    return validator


def is_even() -> Validator:
    """
    Validate that a number is even.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value % 2 != 0:
            raise ValueError("must be even")
        return True

    return validator


def is_odd() -> Validator:
    """
    Validate that a number is odd.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if value % 2 == 0:
            raise ValueError("must be odd")
        return True

    return validator


# ============================================================================
# COLLECTION VALIDATORS
# ============================================================================


def non_empty() -> Validator:
    """
    Validate that a collection (string, list, dict, etc.) is not empty.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not value:
            raise ValueError("must not be empty")
        return True

    return validator


def unique_items() -> Validator:
    """
    Validate that all items in a collection are unique.

    Returns:
        Validator function.
    """

    def validator(value: list[Any] | tuple[Any, ...]) -> bool:
        if len(value) != len(set(value)):
            raise ValueError("all items must be unique")
        return True

    return validator


def has_items(*required_items: Any) -> Validator:
    """
    Validate that a collection contains all required items.

    Args:
        *required_items: Items that must be present.

    Returns:
        Validator function.
    """

    def validator(value: list[Any] | tuple[Any, ...] | set[Any]) -> bool:
        missing = [item for item in required_items if item not in value]
        if missing:
            raise ValueError(f"must contain items: {missing}")
        return True

    return validator


def min_items(min_count: int) -> Validator:
    """
    Validate that a collection has at least minimum number of items.

    Args:
        min_count: Minimum number of items.

    Returns:
        Validator function.
    """

    def validator(value: list[Any] | tuple[Any, ...] | set[Any] | dict[Any, Any]) -> bool:
        if len(value) < min_count:
            raise ValueError(f"must have at least {min_count} items")
        return True

    return validator


def max_items(max_count: int) -> Validator:
    """
    Validate that a collection has at most maximum number of items.

    Args:
        max_count: Maximum number of items.

    Returns:
        Validator function.
    """

    def validator(value: list[Any] | tuple[Any, ...] | set[Any] | dict[Any, Any]) -> bool:
        if len(value) > max_count:
            raise ValueError(f"must have at most {max_count} items")
        return True

    return validator


# ============================================================================
# DICTIONARY VALIDATORS
# ============================================================================


def has_keys(*required_keys: str) -> Validator:
    """
    Validate that a dictionary contains all required keys.

    Args:
        *required_keys: Keys that must be present.

    Returns:
        Validator function.
    """

    def validator(value: dict[Any, Any]) -> bool:
        missing = [key for key in required_keys if key not in value]
        if missing:
            raise ValueError(f"must contain keys: {missing}")
        return True

    return validator


def keys_in(*allowed_keys: str) -> Validator:
    """
    Validate that a dictionary contains only allowed keys.

    Args:
        *allowed_keys: Keys that are allowed.

    Returns:
        Validator function.
    """

    def validator(value: dict[Any, Any]) -> bool:
        invalid = [key for key in value if key not in allowed_keys]
        if invalid:
            raise ValueError(f"invalid keys: {invalid}")
        return True

    return validator


# ============================================================================
# URL VALIDATORS
# ============================================================================


def url_scheme(*schemes: str) -> Validator:
    """
    Validate that a URL has one of the specified schemes.

    Args:
        *schemes: Allowed URL schemes (e.g., 'http', 'https', 'ftp').

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        parsed = urlparse(value)
        if parsed.scheme not in schemes:
            raise ValueError(f"URL scheme must be one of {schemes}, got '{parsed.scheme}'")
        return True

    return validator


def valid_url() -> Validator:
    """
    Validate that a string is a valid URL with scheme and netloc.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("must be a valid URL with scheme and domain")
        return True

    return validator


# ============================================================================
# PATH VALIDATORS
# ============================================================================


def path_exists() -> Validator:
    """
    Validate that a file or directory path exists in the filesystem.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not Path(value).exists():
            raise ValueError(f"path does not exist: {value}")
        return True

    return validator


def is_file() -> Validator:
    """
    Validate that a path points to an existing file.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        path = Path(value)
        if not path.is_file():
            raise ValueError(f"not a file: {value}")
        return True

    return validator


def is_directory() -> Validator:
    """
    Validate that a path points to an existing directory.

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        path = Path(value)
        if not path.is_dir():
            raise ValueError(f"not a directory: {value}")
        return True

    return validator


def is_absolute_path() -> Validator:
    """
    Validate that a path is absolute (not relative).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if not Path(value).is_absolute():
            raise ValueError("path must be absolute")
        return True

    return validator


def is_relative_path() -> Validator:
    """
    Validate that a path is relative (not absolute).

    Returns:
        Validator function.
    """

    def validator(value: Any) -> bool:
        if Path(value).is_absolute():
            raise ValueError("path must be relative")
        return True

    return validator


def file_extension(*extensions: str) -> Validator:
    """
    Validate that a file path has one of the specified extensions.

    Args:
        *extensions: Allowed file extensions (with or without dot).

    Returns:
        Validator function.
    """

    # Normalize extensions to include dot
    normalized = tuple(ext if ext.startswith(".") else f".{ext}" for ext in extensions)

    def validator(value: Any) -> bool:
        path = Path(value)
        if path.suffix not in normalized:
            raise ValueError(f"file extension must be one of {normalized}")
        return True

    return validator

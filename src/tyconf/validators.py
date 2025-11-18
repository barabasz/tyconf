"""
TyConf - Built-in validators for value validation.

This module provides ready-to-use validators for common validation scenarios.
"""

import re
from typing import Any, Callable, Optional


def range(min_val: Optional[int | float] = None, max_val: Optional[int | float] = None) -> Callable:
    """
    Validate that a numeric value is within the specified range.

    Args:
        min_val: Minimum allowed value (inclusive). None means no minimum.
        max_val: Maximum allowed value (inclusive). None means no maximum.

    Returns:
        Validator function.

    Raises:
        ValueError: If value is outside the specified range.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import range
        >>> config = TyConf(port=(int, 8080, range(1024, 65535)))
        >>> config.port = 3000  # OK
        >>> config.port = 80    # ValueError
    """

    def validator(value: int | float) -> bool:
        if min_val is not None and value < min_val:
            raise ValueError(f"must be >= {min_val}")
        if max_val is not None and value > max_val:
            raise ValueError(f"must be <= {max_val}")
        return True

    return validator


def length(min_len: Optional[int] = None, max_len: Optional[int] = None) -> Callable:
    """
    Validate that a string or collection has length within the specified range.

    Args:
        min_len: Minimum allowed length (inclusive). None means no minimum.
        max_len: Maximum allowed length (inclusive). None means no maximum.

    Returns:
        Validator function.

    Raises:
        ValueError: If length is outside the specified range.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import length
        >>> config = TyConf(username=(str, "admin", length(min_len=3, max_len=20)))
        >>> config.username = "john"  # OK
        >>> config.username = "ab"    # ValueError: too short
    """

    def validator(value: Any) -> bool:
        actual_len = len(value)
        if min_len is not None and actual_len < min_len:
            raise ValueError(f"length must be >= {min_len}")
        if max_len is not None and actual_len > max_len:
            raise ValueError(f"length must be <= {max_len}")
        return True

    return validator


def regex(pattern: str) -> Callable:
    """
    Validate that a string matches the specified regular expression pattern.

    Args:
        pattern: Regular expression pattern to match.

    Returns:
        Validator function.

    Raises:
        ValueError: If string doesn't match the pattern.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import regex
        >>> config = TyConf(
        ...     email=(str, "user@example.com", regex(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'))
        ... )
        >>> config.email = "valid@email.com"  # OK
        >>> config.email = "invalid-email"    # ValueError
    """
    compiled = re.compile(pattern)

    def validator(value: str) -> bool:
        if not compiled.match(value):
            raise ValueError(f"must match pattern {pattern}")
        return True

    return validator


def one_of(*allowed_values: Any) -> Callable:
    """
    Validate that a value is one of the allowed values.

    Args:
        *allowed_values: Allowed values.

    Returns:
        Validator function.

    Raises:
        ValueError: If value is not in the allowed set.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import one_of
        >>> config = TyConf(
        ...     log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR"))
        ... )
        >>> config.log_level = "DEBUG"  # OK
        >>> config.log_level = "TRACE"  # ValueError
    """

    def validator(value: Any) -> bool:
        if value not in allowed_values:
            raise ValueError(f"must be one of {allowed_values}")
        return True

    return validator


def all_of(*validators: Callable) -> Callable:
    """
    Combine multiple validators - all must pass.

    Args:
        *validators: Validator functions to combine.

    Returns:
        Combined validator function.

    Raises:
        ValueError: If any validator fails.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import all_of, length, regex
        >>> config = TyConf(
        ...     username=(str, "admin", all_of(
        ...         length(min_len=3, max_len=20),
        ...         regex(r'^[a-zA-Z0-9_]+$')
        ...     ))
        ... )
        >>> config.username = "john_doe"  # OK (passes both validators)
        >>> config.username = "ab"        # ValueError (too short)
        >>> config.username = "john@doe"  # ValueError (invalid characters)
    """

    def validator(value: Any) -> bool:
        for v in validators:
            v(value)  # Will raise ValueError if fails
        return True

    return validator


def any_of(*validators: Callable) -> Callable:
    """
    Combine multiple validators - at least one must pass.

    Args:
        *validators: Validator functions to combine.

    Returns:
        Combined validator function.

    Raises:
        ValueError: If all validators fail.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import any_of, regex
        >>> # Accept email OR phone number format
        >>> config = TyConf(
        ...     contact=(str, "user@example.com", any_of(
        ...         regex(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'),  # email
        ...         regex(r'^\\+?[0-9]{9,15}$')             # phone
        ...     ))
        ... )
        >>> config.contact = "user@example.com"  # OK (email)
        >>> config.contact = "+48123456789"      # OK (phone)
        >>> config.contact = "invalid"           # ValueError (neither)
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


def not_in(*disallowed_values: Any) -> Callable:
    """
    Validate that a value is NOT in the disallowed set.

    Args:
        *disallowed_values: Disallowed values.

    Returns:
        Validator function.

    Raises:
        ValueError: If value is in the disallowed set.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import not_in, all_of, range
        >>> # Port in valid range but not reserved
        >>> config = TyConf(
        ...     port=(int, 8080, all_of(
        ...         range(1024, 65535),
        ...         not_in(3000, 5000, 8000)  # reserved ports
        ...     ))
        ... )
        >>> config.port = 8080  # OK
        >>> config.port = 3000  # ValueError (reserved)
    """

    def validator(value: Any) -> bool:
        if value in disallowed_values:
            raise ValueError(f"must not be one of {disallowed_values}")
        return True

    return validator

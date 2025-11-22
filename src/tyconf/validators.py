"""
TyConf - Built-in validators for value validation.

This module provides ready-to-use validators for common validation scenarios.
"""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# ============================================================================
# COMBINATOR VALIDATORS - Combine multiple validators
# ============================================================================


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


# ============================================================================
# CHOICE VALIDATORS - Validate against allowed/disallowed values
# ============================================================================


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
        ...     log_level=(str, "INFO",
        ...                one_of("DEBUG", "INFO", "WARNING", "ERROR"))
        ... )
        >>> config.log_level = "DEBUG"  # OK
        >>> config.log_level = "TRACE"  # ValueError
    """

    def validator(value: Any) -> bool:
        if value not in allowed_values:
            raise ValueError(f"must be one of {allowed_values}")
        return True

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


# ============================================================================
# STRING VALIDATORS - Length
# ============================================================================


def length(min_len: int | None = None, max_len: int | None = None) -> Callable:
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
        >>> config = TyConf(
        ...     username=(str, "admin", length(min_len=3, max_len=20))
        ... )
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


def min_length(min_len: int) -> Callable:
    """
    Validate that a string or collection has minimum length.

    Simplified version of length() for when only minimum is needed.

    Args:
        min_len: Minimum allowed length (inclusive).

    Returns:
        Validator function.

    Raises:
        ValueError: If length is less than minimum.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import min_length
        >>> config = TyConf(password=(str, "secret123", min_length(8)))
        >>> config.password = "short"  # ValueError
    """

    def validator(value: Any) -> bool:
        if len(value) < min_len:
            raise ValueError(f"length must be >= {min_len}")
        return True

    return validator


def max_length(max_len: int) -> Callable:
    """
    Validate that a string or collection has maximum length.

    Simplified version of length() for when only maximum is needed.

    Args:
        max_len: Maximum allowed length (inclusive).

    Returns:
        Validator function.

    Raises:
        ValueError: If length exceeds maximum.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import max_length
        >>> config = TyConf(code=(str, "ABC", max_length(10)))
        >>> config.code = "VERYLONGCODE"  # ValueError
    """

    def validator(value: Any) -> bool:
        if len(value) > max_len:
            raise ValueError(f"length must be <= {max_len}")
        return True

    return validator


# ============================================================================
# STRING VALIDATORS - Content matching
# ============================================================================


def contains(substring: str, case_sensitive: bool = True) -> Callable:
    """
    Validate that a string contains a specific substring.

    Args:
        substring: The string that must be present.
        case_sensitive: Whether matching should be case-sensitive.

    Returns:
        Validator function.

    Raises:
        ValueError: If substring is not found.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import contains
        >>> config = TyConf(path=(str, "/var/log", contains("/log")))
        >>> config = TyConf(mode=(str, "DEBUG", contains("debug", case_sensitive=False)))
    """

    def validator(value: str) -> bool:
        val_to_check = value if case_sensitive else value.lower()
        sub_to_check = substring if case_sensitive else substring.lower()

        if sub_to_check not in val_to_check:
            msg = f"must contain '{substring}'"
            if not case_sensitive:
                msg += " (case insensitive)"
            raise ValueError(msg)
        return True

    return validator


def starts_with(prefix: str, case_sensitive: bool = True) -> Callable:
    """
    Validate that a string starts with the specified prefix.

    Args:
        prefix: Required prefix string.
        case_sensitive: Whether matching should be case-sensitive (default: True).

    Returns:
        Validator function.

    Raises:
        ValueError: If string doesn't start with prefix.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import starts_with
        >>> config = TyConf(
        ...     api_url=(str, "https://api.example.com", starts_with("https://"))
        ... )
        >>> config.api_url = "https://api.test.com"  # OK
        >>> config.api_url = "http://api.test.com"   # ValueError
    """

    def validator(value: str) -> bool:
        val_to_check = value if case_sensitive else value.lower()
        prefix_to_check = prefix if case_sensitive else prefix.lower()

        if not val_to_check.startswith(prefix_to_check):
            msg = f"must start with '{prefix}'"
            if not case_sensitive:
                msg += " (case insensitive)"
            raise ValueError(msg)
        return True

    return validator


def ends_with(suffix: str, case_sensitive: bool = True) -> Callable:
    """
    Validate that a string ends with the specified suffix.

    Args:
        suffix: Required suffix string.
        case_sensitive: Whether matching should be case-sensitive (default: True).

    Returns:
        Validator function.

    Raises:
        ValueError: If string doesn't end with suffix.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import ends_with
        >>> config = TyConf(
        ...     log_file=(str, "app.log", ends_with(".log"))
        ... )
        >>> config.log_file = "error.log"  # OK
        >>> config.log_file = "app.txt"    # ValueError
    """

    def validator(value: str) -> bool:
        val_to_check = value if case_sensitive else value.lower()
        suffix_to_check = suffix if case_sensitive else suffix.lower()

        if not val_to_check.endswith(suffix_to_check):
            msg = f"must end with '{suffix}'"
            if not case_sensitive:
                msg += " (case insensitive)"
            raise ValueError(msg)
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
        ...     email=(str, "user@example.com",
        ...            regex(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'))
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


# ============================================================================
# STRING VALIDATORS - Character type
# ============================================================================


def is_alpha() -> Callable:
    """
    Validate that a string contains only alphabetic characters.

    Returns:
        Validator function.

    Raises:
        ValueError: If string contains non-alphabetic characters.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_alpha
        >>> config = TyConf(name=(str, "John", is_alpha()))
        >>> config.name = "Alice"  # OK
        >>> config.name = "John123"  # ValueError
    """

    def validator(value: str) -> bool:
        if not value.isalpha():
            raise ValueError("must contain only alphabetic characters")
        return True

    return validator


def is_alphanumeric() -> Callable:
    """
    Validate that a string contains only alphanumeric characters.

    Returns:
        Validator function.

    Raises:
        ValueError: If string contains non-alphanumeric characters.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_alphanumeric
        >>> config = TyConf(username=(str, "user123", is_alphanumeric()))
        >>> config.username = "admin456"  # OK
        >>> config.username = "user_123"  # ValueError (underscore not allowed)
    """

    def validator(value: str) -> bool:
        if not value.isalnum():
            raise ValueError("must contain only alphanumeric characters")
        return True

    return validator


def is_numeric() -> Callable:
    """
    Validate that a string contains only numeric characters.

    Returns:
        Validator function.

    Raises:
        ValueError: If string contains non-numeric characters.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_numeric
        >>> config = TyConf(code=(str, "12345", is_numeric()))
        >>> config.code = "98765"  # OK
        >>> config.code = "123abc"  # ValueError
    """

    def validator(value: str) -> bool:
        if not value.isdigit():
            raise ValueError("must contain only numeric characters")
        return True

    return validator


def is_lowercase() -> Callable:
    """
    Validate that a string contains only lowercase characters.

    Returns:
        Validator function.

    Raises:
        ValueError: If string contains uppercase characters.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_lowercase
        >>> config = TyConf(username=(str, "admin", is_lowercase()))
        >>> config.username = "johndoe"  # OK
        >>> config.username = "JohnDoe"  # ValueError
    """

    def validator(value: str) -> bool:
        if not value.islower():
            raise ValueError("must be lowercase")
        return True

    return validator


def is_uppercase() -> Callable:
    """
    Validate that a string contains only uppercase characters.

    Returns:
        Validator function.

    Raises:
        ValueError: If string contains lowercase characters.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_uppercase
        >>> config = TyConf(code=(str, "ABC", is_uppercase()))
        >>> config.code = "XYZ"  # OK
        >>> config.code = "xyz"  # ValueError
    """

    def validator(value: str) -> bool:
        if not value.isupper():
            raise ValueError("must be uppercase")
        return True

    return validator


def no_whitespace() -> Callable:
    """
    Validate that a string contains no whitespace characters.

    Useful for usernames, tokens, identifiers, etc.

    Returns:
        Validator function.

    Raises:
        ValueError: If string contains whitespace.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import no_whitespace
        >>> config = TyConf(username=(str, "admin", no_whitespace()))
        >>> config.username = "john_doe"  # OK
        >>> config.username = "john doe"  # ValueError
    """

    def validator(value: str) -> bool:
        if any(c.isspace() for c in value):
            raise ValueError("must not contain whitespace")
        return True

    return validator


# ============================================================================
# NUMERIC VALIDATORS - Range
# ============================================================================


def range(min_val: int | float | None = None, max_val: int | float | None = None) -> Callable:
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


def between(min_val: int | float, max_val: int | float, inclusive: bool = True) -> Callable:
    """
    Validate that a numeric value is between min and max.

    Args:
        min_val: Minimum value.
        max_val: Maximum value.
        inclusive: If True, includes boundaries (default: True).

    Returns:
        Validator function.

    Raises:
        ValueError: If value is outside range.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import between
        >>> config = TyConf(
        ...     percentage=(int, 50, between(0, 100)),
        ...     temperature=(float, 20.5, between(15.0, 25.0, inclusive=False))
        ... )
    """

    def validator(value: int | float) -> bool:
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


def positive() -> Callable:
    """
    Validate that a number is positive (> 0).

    Returns:
        Validator function.

    Raises:
        ValueError: If number is not positive.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import positive
        >>> config = TyConf(timeout=(int, 30, positive()))
        >>> config.timeout = 60   # OK
        >>> config.timeout = 0    # ValueError
        >>> config.timeout = -10  # ValueError
    """

    def validator(value: int | float) -> bool:
        if value <= 0:
            raise ValueError("must be positive (> 0)")
        return True

    return validator


def negative() -> Callable:
    """
    Validate that a number is negative (< 0).

    Returns:
        Validator function.

    Raises:
        ValueError: If number is not negative.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import negative
        >>> config = TyConf(temperature=(float, -5.0, negative()))
        >>> config.temperature = -10.0  # OK
        >>> config.temperature = 0      # ValueError
    """

    def validator(value: int | float) -> bool:
        if value >= 0:
            raise ValueError("must be negative (< 0)")
        return True

    return validator


def non_negative() -> Callable:
    """
    Validate that a number is non-negative (>= 0).

    Returns:
        Validator function.

    Raises:
        ValueError: If number is negative.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import non_negative
        >>> config = TyConf(count=(int, 0, non_negative()))
        >>> config.count = 0    # OK
        >>> config.count = 100  # OK
        >>> config.count = -1   # ValueError
    """

    def validator(value: int | float) -> bool:
        if value < 0:
            raise ValueError("must be non-negative (>= 0)")
        return True

    return validator


def non_positive() -> Callable:
    """
    Validate that a number is non-positive (<= 0).

    Returns:
        Validator function.

    Raises:
        ValueError: If number is positive.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import non_positive
        >>> config = TyConf(debt=(float, -100.0, non_positive()))
        >>> config.debt = 0      # OK
        >>> config.debt = -50.0  # OK
        >>> config.debt = 10.0   # ValueError
    """

    def validator(value: int | float) -> bool:
        if value > 0:
            raise ValueError("must be non-positive (<= 0)")
        return True

    return validator


# ============================================================================
# NUMERIC VALIDATORS - Divisibility and parity
# ============================================================================


def divisible_by(divisor: int) -> Callable:
    """
    Validate that a number is divisible by the specified divisor.

    Args:
        divisor: The number that value must be divisible by.

    Returns:
        Validator function.

    Raises:
        ValueError: If number is not divisible by divisor.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import divisible_by
        >>> config = TyConf(port=(int, 8080, divisible_by(10)))
        >>> config.port = 8080  # OK (divisible by 10)
        >>> config.port = 8081  # ValueError
    """

    def validator(value: int) -> bool:
        if value % divisor != 0:
            raise ValueError(f"must be divisible by {divisor}")
        return True

    return validator


def is_even() -> Callable:
    """
    Validate that a number is even.

    Returns:
        Validator function.

    Raises:
        ValueError: If number is not even.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_even
        >>> config = TyConf(threads=(int, 4, is_even()))
        >>> config.threads = 8   # OK
        >>> config.threads = 5   # ValueError
    """

    def validator(value: int) -> bool:
        if value % 2 != 0:
            raise ValueError("must be even")
        return True

    return validator


def is_odd() -> Callable:
    """
    Validate that a number is odd.

    Returns:
        Validator function.

    Raises:
        ValueError: If number is not odd.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_odd
        >>> config = TyConf(retries=(int, 3, is_odd()))
        >>> config.retries = 5  # OK
        >>> config.retries = 4  # ValueError
    """

    def validator(value: int) -> bool:
        if value % 2 == 0:
            raise ValueError("must be odd")
        return True

    return validator


# ============================================================================
# COLLECTION VALIDATORS
# ============================================================================


def non_empty() -> Callable:
    """
    Validate that a collection (string, list, dict, etc.) is not empty.

    Returns:
        Validator function.

    Raises:
        ValueError: If collection is empty.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import non_empty
        >>> config = TyConf(
        ...     tags=(list, ["python"], non_empty()),
        ...     name=(str, "app", non_empty())
        ... )
        >>> config.tags = ["python", "config"]  # OK
        >>> config.tags = []                     # ValueError
    """

    def validator(value: Any) -> bool:
        if not value:
            raise ValueError("must not be empty")
        return True

    return validator


def unique_items() -> Callable:
    """
    Validate that all items in a collection are unique.

    Returns:
        Validator function.

    Raises:
        ValueError: If collection contains duplicate items.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import unique_items
        >>> config = TyConf(tags=(list, ["a", "b"], unique_items()))
        >>> config.tags = ["x", "y", "z"]  # OK
        >>> config.tags = ["x", "y", "x"]  # ValueError (duplicate 'x')
    """

    def validator(value: list | tuple) -> bool:
        if len(value) != len(set(value)):
            raise ValueError("all items must be unique")
        return True

    return validator


def has_items(*required_items: Any) -> Callable:
    """
    Validate that a collection contains all required items.

    Args:
        *required_items: Items that must be present.

    Returns:
        Validator function.

    Raises:
        ValueError: If any required item is missing.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import has_items
        >>> config = TyConf(
        ...     features=(list, ["api", "web"], has_items("api"))
        ... )
        >>> config.features = ["api", "web", "cli"]  # OK
        >>> config.features = ["web", "cli"]          # ValueError
    """

    def validator(value: list | tuple | set) -> bool:
        missing = [item for item in required_items if item not in value]
        if missing:
            raise ValueError(f"must contain items: {missing}")
        return True

    return validator


def min_items(min_count: int) -> Callable:
    """
    Validate that a collection has at least minimum number of items.

    Args:
        min_count: Minimum number of items.

    Returns:
        Validator function.

    Raises:
        ValueError: If collection has fewer items.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import min_items
        >>> config = TyConf(servers=(list, ["srv1", "srv2"], min_items(2)))
        >>> config.servers = ["srv1"]  # ValueError
    """

    def validator(value: list | tuple | set | dict) -> bool:
        if len(value) < min_count:
            raise ValueError(f"must have at least {min_count} items")
        return True

    return validator


def max_items(max_count: int) -> Callable:
    """
    Validate that a collection has at most maximum number of items.

    Args:
        max_count: Maximum number of items.

    Returns:
        Validator function.

    Raises:
        ValueError: If collection has more items.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import max_items
        >>> config = TyConf(tags=(list, ["a", "b"], max_items(5)))
        >>> config.tags = ["a", "b", "c", "d", "e", "f"]  # ValueError
    """

    def validator(value: list | tuple | set | dict) -> bool:
        if len(value) > max_count:
            raise ValueError(f"must have at most {max_count} items")
        return True

    return validator


# ============================================================================
# DICTIONARY VALIDATORS
# ============================================================================


def has_keys(*required_keys: str) -> Callable:
    """
    Validate that a dictionary contains all required keys.

    Args:
        *required_keys: Keys that must be present.

    Returns:
        Validator function.

    Raises:
        ValueError: If any required key is missing.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import has_keys
        >>> config = TyConf(
        ...     db_config=(dict, {"host": "localhost"}, has_keys("host", "port"))
        ... )
    """

    def validator(value: dict) -> bool:
        missing = [key for key in required_keys if key not in value]
        if missing:
            raise ValueError(f"must contain keys: {missing}")
        return True

    return validator


def keys_in(*allowed_keys: str) -> Callable:
    """
    Validate that a dictionary contains only allowed keys.

    Args:
        *allowed_keys: Keys that are allowed.

    Returns:
        Validator function.

    Raises:
        ValueError: If any key is not allowed.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import keys_in
        >>> config = TyConf(
        ...     options=(dict, {"debug": True}, keys_in("debug", "verbose"))
        ... )
    """

    def validator(value: dict) -> bool:
        invalid = [key for key in value if key not in allowed_keys]
        if invalid:
            raise ValueError(f"invalid keys: {invalid}")
        return True

    return validator


# ============================================================================
# URL VALIDATORS
# ============================================================================


def url_scheme(*schemes: str) -> Callable:
    """
    Validate that a URL has one of the specified schemes.

    Args:
        *schemes: Allowed URL schemes (e.g., 'http', 'https', 'ftp').

    Returns:
        Validator function.

    Raises:
        ValueError: If URL scheme is not in allowed schemes.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import url_scheme
        >>> config = TyConf(
        ...     api_url=(str, "https://api.example.com", url_scheme("https"))
        ... )
        >>> config.api_url = "https://secure.com"  # OK
        >>> config.api_url = "http://insecure.com" # ValueError
    """

    def validator(value: str) -> bool:
        parsed = urlparse(value)
        if parsed.scheme not in schemes:
            raise ValueError(f"URL scheme must be one of {schemes}, got '{parsed.scheme}'")
        return True

    return validator


def valid_url() -> Callable:
    """
    Validate that a string is a valid URL with scheme and netloc.

    Returns:
        Validator function.

    Raises:
        ValueError: If URL is invalid.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import valid_url
        >>> config = TyConf(website=(str, "https://example.com", valid_url()))
        >>> config.website = "https://example.com"  # OK
        >>> config.website = "not-a-url"            # ValueError
    """

    def validator(value: str) -> bool:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("must be a valid URL with scheme and domain")
        return True

    return validator


# ============================================================================
# PATH VALIDATORS
# ============================================================================


def path_exists() -> Callable:
    """
    Validate that a file or directory path exists in the filesystem.

    Returns:
        Validator function.

    Raises:
        ValueError: If path does not exist.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import path_exists
        >>> config = TyConf(config_file=(str, "/etc/app.conf", path_exists()))
    """

    def validator(value: str) -> bool:
        if not Path(value).exists():
            raise ValueError(f"path does not exist: {value}")
        return True

    return validator


def is_file() -> Callable:
    """
    Validate that a path points to an existing file.

    Returns:
        Validator function.

    Raises:
        ValueError: If path is not a file.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_file
        >>> config = TyConf(config_file=(str, "config.json", is_file()))
    """

    def validator(value: str) -> bool:
        path = Path(value)
        if not path.is_file():
            raise ValueError(f"not a file: {value}")
        return True

    return validator


def is_directory() -> Callable:
    """
    Validate that a path points to an existing directory.

    Returns:
        Validator function.

    Raises:
        ValueError: If path is not a directory.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_directory
        >>> config = TyConf(data_dir=(str, "/var/data", is_directory()))
    """

    def validator(value: str) -> bool:
        path = Path(value)
        if not path.is_dir():
            raise ValueError(f"not a directory: {value}")
        return True

    return validator


def is_absolute_path() -> Callable:
    """
    Validate that a path is absolute (not relative).

    Returns:
        Validator function.

    Raises:
        ValueError: If path is not absolute.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_absolute_path
        >>> config = TyConf(install_dir=(str, "/opt/app", is_absolute_path()))
        >>> config.install_dir = "/usr/local/app"  # OK
        >>> config.install_dir = "relative/path"   # ValueError
    """

    def validator(value: str) -> bool:
        if not Path(value).is_absolute():
            raise ValueError("path must be absolute")
        return True

    return validator


def is_relative_path() -> Callable:
    """
    Validate that a path is relative (not absolute).

    Returns:
        Validator function.

    Raises:
        ValueError: If path is not relative.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import is_relative_path
        >>> config = TyConf(config_path=(str, "config/app.conf", is_relative_path()))
        >>> config.config_path = "data/file.txt"  # OK
        >>> config.config_path = "/etc/file.txt"  # ValueError
    """

    def validator(value: str) -> bool:
        if Path(value).is_absolute():
            raise ValueError("path must be relative")
        return True

    return validator


def file_extension(*extensions: str) -> Callable:
    """
    Validate that a file path has one of the specified extensions.

    Args:
        *extensions: Allowed file extensions (with or without dot).

    Returns:
        Validator function.

    Raises:
        ValueError: If file extension is not in allowed extensions.

    Examples:
        >>> from tyconf import TyConf
        >>> from tyconf.validators import file_extension
        >>> config = TyConf(
        ...     config_file=(str, "app.json", file_extension(".json", ".yaml"))
        ... )
        >>> config.config_file = "settings.yaml"  # OK
        >>> config.config_file = "data.xml"       # ValueError
    """

    # Normalize extensions to include dot
    normalized = tuple(ext if ext.startswith(".") else f".{ext}" for ext in extensions)

    def validator(value: str) -> bool:
        path = Path(value)
        if path.suffix not in normalized:
            raise ValueError(f"file extension must be one of {normalized}")
        return True

    return validator

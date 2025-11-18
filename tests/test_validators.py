"""Tests for TyConf validators."""

import pytest
from tyconf import TyConf
from tyconf.validators import range, length, regex, one_of, all_of, any_of, not_in


def test_range_validator():
    """Test range validator with min and max."""
    config = TyConf(port=(int, 8080, range(1024, 65535)))

    # Valid values
    config.port = 1024  # Min
    config.port = 65535  # Max
    config.port = 3000  # Middle

    # Invalid values
    with pytest.raises(ValueError, match="must be >= 1024"):
        config.port = 80

    with pytest.raises(ValueError, match="must be <= 65535"):
        config.port = 70000


def test_range_validator_min_only():
    """Test range validator with only minimum."""
    config = TyConf(age=(int, 18, range(min_val=0)))

    config.age = 0
    config.age = 100

    with pytest.raises(ValueError, match="must be >= 0"):
        config.age = -1


def test_range_validator_max_only():
    """Test range validator with only maximum."""
    config = TyConf(percentage=(int, 50, range(max_val=100)))

    config.percentage = 0
    config.percentage = 100

    with pytest.raises(ValueError, match="must be <= 100"):
        config.percentage = 101


def test_range_validator_float():
    """Test range validator with float values."""
    config = TyConf(temperature=(float, 20.5, range(-273.15, 1000.0)))

    config.temperature = -273.15
    config.temperature = 36.6
    config.temperature = 1000.0

    with pytest.raises(ValueError, match="must be >="):
        config.temperature = -300.0


def test_length_validator():
    """Test length validator with min and max."""
    config = TyConf(username=(str, "admin", length(min_len=3, max_len=20)))

    # Valid values
    config.username = "abc"  # Min
    config.username = "a" * 20  # Max
    config.username = "john_doe"  # Middle

    # Invalid values
    with pytest.raises(ValueError, match="length must be >= 3"):
        config.username = "ab"

    with pytest.raises(ValueError, match="length must be <= 20"):
        config.username = "a" * 21


def test_length_validator_min_only():
    """Test length validator with only minimum."""
    config = TyConf(password=(str, "secret123", length(min_len=8)))

    config.password = "12345678"
    config.password = "very_long_password"

    with pytest.raises(ValueError, match="length must be >= 8"):
        config.password = "short"


def test_length_validator_max_only():
    """Test length validator with only maximum."""
    config = TyConf(code=(str, "ABC", length(max_len=10)))

    config.code = "A"
    config.code = "A" * 10

    with pytest.raises(ValueError, match="length must be <= 10"):
        config.code = "A" * 11


def test_length_validator_list():
    """Test length validator with lists."""
    config = TyConf(tags=(list, ["a", "b"], length(min_len=1, max_len=5)))

    config.tags = ["x"]
    config.tags = ["a", "b", "c", "d", "e"]

    with pytest.raises(ValueError, match="length must be >= 1"):
        config.tags = []

    with pytest.raises(ValueError, match="length must be <= 5"):
        config.tags = ["a", "b", "c", "d", "e", "f"]


def test_regex_validator():
    """Test regex validator."""
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    config = TyConf(email=(str, "user@example.com", regex(email_pattern)))

    # Valid emails
    config.email = "user@example.com"
    config.email = "john.doe@company.co.uk"
    config.email = "test_user@domain.org"

    # Invalid emails
    with pytest.raises(ValueError, match="must match pattern"):
        config.email = "invalid-email"

    with pytest.raises(ValueError, match="must match pattern"):
        config.email = "@example.com"


def test_regex_validator_phone():
    """Test regex validator with phone numbers."""
    phone_pattern = r"^\+?[0-9]{9,15}$"
    config = TyConf(phone=(str, "+48123456789", regex(phone_pattern)))

    config.phone = "123456789"
    config.phone = "+48123456789"
    config.phone = "1234567890123"

    with pytest.raises(ValueError, match="must match pattern"):
        config.phone = "12345"  # Too short

    with pytest.raises(ValueError, match="must match pattern"):
        config.phone = "abc123"  # Letters


def test_one_of_validator():
    """Test one_of validator."""
    config = TyConf(log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR")))

    # Valid values
    config.log_level = "DEBUG"
    config.log_level = "INFO"
    config.log_level = "WARNING"
    config.log_level = "ERROR"

    # Invalid value
    with pytest.raises(ValueError, match="must be one of"):
        config.log_level = "TRACE"


def test_one_of_validator_numbers():
    """Test one_of validator with numbers."""
    config = TyConf(choice=(int, 1, one_of(1, 2, 3, 5, 8, 13)))

    config.choice = 1
    config.choice = 5
    config.choice = 13

    with pytest.raises(ValueError, match="must be one of"):
        config.choice = 4


def test_all_of_validator():
    """Test all_of validator combining multiple validators."""
    config = TyConf(
        username=(str, "admin", all_of(length(min_len=3, max_len=20), regex(r"^[a-zA-Z0-9_]+$")))
    )

    # Valid usernames
    config.username = "abc"
    config.username = "john_doe"
    config.username = "User123"

    # Too short
    with pytest.raises(ValueError, match="length must be >= 3"):
        config.username = "ab"

    # Invalid characters
    with pytest.raises(ValueError, match="must match pattern"):
        config.username = "john@doe"


def test_all_of_validator_three_validators():
    """Test all_of with three validators."""

    def must_be_multiple_of_10(x):
        if x % 10 != 0:
            raise ValueError("must be multiple of 10")
        return True

    config = TyConf(
        port=(
            int,
            8080,
            all_of(
                range(1024, 65535),
                not_in(3000, 5000),
                must_be_multiple_of_10,  # Użyj funkcji zamiast lambdy
            ),
        )
    )

    config.port = 8080  # Valid
    config.port = 2000  # Valid

    # Out of range
    with pytest.raises(ValueError, match="must be >= 1024"):
        config.port = 80

    # Reserved
    with pytest.raises(ValueError, match="must not be one of"):
        config.port = 3000

    # Not multiple of 10
    with pytest.raises(ValueError, match="must be multiple of 10"):
        config.port = 8081


def test_any_of_validator():
    """Test any_of validator."""
    config = TyConf(
        contact=(
            str,
            "user@example.com",
            any_of(
                regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"), regex(r"^\+?[0-9]{9,15}$")  # Email  # Phone
            ),
        )
    )

    # Valid email
    config.contact = "user@example.com"

    # Valid phone
    config.contact = "+48123456789"
    config.contact = "123456789"

    # Neither email nor phone
    with pytest.raises(ValueError, match="must satisfy at least one of"):
        config.contact = "invalid"


def test_not_in_validator():
    """Test not_in validator."""
    config = TyConf(port=(int, 8080, not_in(3000, 5000, 8000)))

    # Valid ports
    config.port = 8080
    config.port = 9000
    config.port = 1024

    # Reserved ports
    with pytest.raises(ValueError, match="must not be one of"):
        config.port = 3000

    with pytest.raises(ValueError, match="must not be one of"):
        config.port = 5000


def test_validator_with_lambda():
    """Test using lambda as validator."""
    config = TyConf(percentage=(int, 50, lambda x: 0 <= x <= 100))

    config.percentage = 0
    config.percentage = 50
    config.percentage = 100

    with pytest.raises(ValueError, match="validation failed"):
        config.percentage = 101


def test_validator_with_custom_function():
    """Test using custom function as validator."""

    def validate_even(value):
        if value % 2 != 0:
            raise ValueError("must be even number")
        return True

    config = TyConf(even_number=(int, 10, validate_even))

    config.even_number = 2
    config.even_number = 100

    with pytest.raises(ValueError, match="must be even number"):
        config.even_number = 3


def test_validator_on_initialization():
    """Test that validator is called on initialization."""
    # Should succeed
    config = TyConf(port=(int, 8080, range(1024, 65535)))
    assert config.port == 8080

    # Should fail
    with pytest.raises(ValueError, match="must be >= 1024"):
        TyConf(port=(int, 80, range(1024, 65535)))


def test_validator_with_none_return():
    """Test validator that returns None (treated as success)."""

    def validator(value):
        if value < 0:
            raise ValueError("must be non-negative")
        # Returns None implicitly

    config = TyConf(count=(int, 5, validator))

    config.count = 0
    config.count = 10

    with pytest.raises(ValueError, match="must be non-negative"):
        config.count = -1


def test_complex_validation_scenario():
    """Test complex real-world validation scenario."""
    config = TyConf(
        # Simple lambda
        percentage=(int, 50, lambda x: 0 <= x <= 100),
        # Built-in validator
        port=(int, 8080, range(1024, 65535)),
        # Combined validators
        username=(str, "admin", all_of(length(min_len=3, max_len=20), regex(r"^[a-zA-Z0-9_]+$"))),
        # Choice validator
        environment=(str, "dev", one_of("dev", "staging", "prod")),
        # No validator
        debug=(bool, True),
    )

    # All valid
    config.percentage = 75
    config.port = 3000
    config.username = "john_doe"
    config.environment = "prod"
    config.debug = False

    # Test failures
    with pytest.raises(ValueError):
        config.percentage = 150

    with pytest.raises(ValueError):
        config.port = 80

    with pytest.raises(ValueError):
        config.username = "ab"

    with pytest.raises(ValueError):
        config.environment = "test"

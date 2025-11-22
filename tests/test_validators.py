"""Tests for TyConf validators."""

import pytest

from tyconf import TyConf
from tyconf.validators import (
    # Combinators
    all_of,
    any_of,
    between,
    # String validators - Content
    contains,
    # Numeric validators - Divisibility
    divisible_by,
    ends_with,
    file_extension,
    has_items,
    # Dictionary validators
    has_keys,
    is_absolute_path,
    # String validators - Character type
    is_alpha,
    is_alphanumeric,
    is_directory,
    is_even,
    is_file,
    is_lowercase,
    is_numeric,
    is_odd,
    is_relative_path,
    is_uppercase,
    keys_in,
    # String validators - Length
    length,
    max_items,
    max_length,
    min_items,
    min_length,
    negative,
    no_whitespace,
    # Collection validators
    non_empty,
    non_negative,
    non_positive,
    not_in,
    # Choice validators
    one_of,
    # Path validators
    path_exists,
    # Numeric validators - Sign
    positive,
    # Numeric validators - Range
    range,
    regex,
    starts_with,
    unique_items,
    # URL validators
    url_scheme,
    valid_url,
)

# ============================================================================
# COMBINATOR VALIDATORS
# ============================================================================


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
                must_be_multiple_of_10,
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
                regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"),  # Email
                regex(r"^\+?[0-9]{9,15}$"),  # Phone
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


# ============================================================================
# CHOICE VALIDATORS
# ============================================================================


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


# ============================================================================
# STRING VALIDATORS - Length
# ============================================================================


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


def test_min_length_validator():
    """Test min_length validator."""
    config = TyConf(password=(str, "secret123", min_length(8)))

    config.password = "12345678"  # Exactly 8
    config.password = "verylongpassword"  # More than 8

    with pytest.raises(ValueError, match="length must be >= 8"):
        config.password = "short"


def test_max_length_validator():
    """Test max_length validator."""
    config = TyConf(code=(str, "ABC", max_length(10)))

    config.code = "A"  # Less than 10
    config.code = "A" * 10  # Exactly 10

    with pytest.raises(ValueError, match="length must be <= 10"):
        config.code = "A" * 11


# ============================================================================
# STRING VALIDATORS - Content matching
# ============================================================================


def test_contains_validator():
    """Test contains validator."""
    config = TyConf(
        path=(str, "/usr/local/bin", contains("local")),
        email=(str, "admin@company.com", contains("@")),
    )

    # Success
    config.path = "/opt/local/bin"
    assert config.path == "/opt/local/bin"

    # Failure
    with pytest.raises(ValueError, match="must contain 'local'"):
        config.path = "/usr/bin/python"


def test_contains_validator_case_insensitive():
    """Test contains validator with case_sensitive=False."""
    config = TyConf(tags=(str, "Urgent-Task", contains("urgent", case_sensitive=False)))

    # Success (mixed case)
    config.tags = "URGENT-TASK"
    config.tags = "very urgent"

    # Failure
    with pytest.raises(ValueError, match="must contain 'urgent'"):
        config.tags = "regular-task"


def test_starts_with_validator():
    """Test starts_with validator."""
    config = TyConf(api_url=(str, "https://api.example.com", starts_with("https://")))

    config.api_url = "https://api.test.com"  # OK

    with pytest.raises(ValueError, match="must start with 'https://'"):
        config.api_url = "http://api.test.com"


def test_starts_with_case_insensitive():
    """Test starts_with validator with case insensitive."""
    config = TyConf(name=(str, "Mr. Smith", starts_with("mr", case_sensitive=False)))

    config.name = "Mr. Jones"  # OK
    config.name = "MR. Brown"  # OK

    with pytest.raises(ValueError):
        config.name = "Dr. Smith"


def test_ends_with_validator():
    """Test ends_with validator."""
    config = TyConf(log_file=(str, "app.log", ends_with(".log")))

    config.log_file = "error.log"  # OK
    config.log_file = "access.log"  # OK

    with pytest.raises(ValueError, match="must end with '.log'"):
        config.log_file = "app.txt"


def test_ends_with_case_insensitive():
    """Test ends_with validator with case insensitive."""
    config = TyConf(filename=(str, "document.PDF", ends_with(".pdf", case_sensitive=False)))

    config.filename = "file.PDF"  # OK
    config.filename = "file.pdf"  # OK

    with pytest.raises(ValueError):
        config.filename = "file.txt"


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


# ============================================================================
# STRING VALIDATORS - Character type
# ============================================================================


def test_is_alpha_validator():
    """Test is_alpha validator."""
    config = TyConf(name=(str, "John", is_alpha()))

    config.name = "Alice"  # OK
    config.name = "Mary"  # OK

    with pytest.raises(ValueError, match="must contain only alphabetic characters"):
        config.name = "John123"

    with pytest.raises(ValueError, match="must contain only alphabetic characters"):
        config.name = "John-Doe"


def test_is_alphanumeric_validator():
    """Test is_alphanumeric validator."""
    config = TyConf(username=(str, "user123", is_alphanumeric()))

    config.username = "admin456"  # OK
    config.username = "test789"  # OK

    with pytest.raises(ValueError, match="must contain only alphanumeric characters"):
        config.username = "user_123"  # Underscore not allowed

    with pytest.raises(ValueError, match="must contain only alphanumeric characters"):
        config.username = "user-123"


def test_is_numeric_validator():
    """Test is_numeric validator."""
    config = TyConf(code=(str, "12345", is_numeric()))

    config.code = "98765"  # OK
    config.code = "00000"  # OK

    with pytest.raises(ValueError, match="must contain only numeric characters"):
        config.code = "123abc"

    with pytest.raises(ValueError, match="must contain only numeric characters"):
        config.code = "123.45"


def test_is_lowercase_validator():
    """Test is_lowercase validator."""
    config = TyConf(username=(str, "admin", is_lowercase()))

    config.username = "johndoe"  # OK
    config.username = "test"  # OK

    with pytest.raises(ValueError, match="must be lowercase"):
        config.username = "JohnDoe"

    with pytest.raises(ValueError, match="must be lowercase"):
        config.username = "Admin"


def test_is_uppercase_validator():
    """Test is_uppercase validator."""
    config = TyConf(code=(str, "ABC", is_uppercase()))

    config.code = "XYZ"  # OK
    config.code = "TEST"  # OK

    with pytest.raises(ValueError, match="must be uppercase"):
        config.code = "xyz"

    with pytest.raises(ValueError, match="must be uppercase"):
        config.code = "Test"


def test_no_whitespace_validator():
    """Test no_whitespace validator."""
    config = TyConf(username=(str, "admin", no_whitespace()))

    config.username = "john_doe"  # OK
    config.username = "test123"  # OK

    with pytest.raises(ValueError, match="must not contain whitespace"):
        config.username = "john doe"

    with pytest.raises(ValueError, match="must not contain whitespace"):
        config.username = "test user"


# ============================================================================
# NUMERIC VALIDATORS - Range
# ============================================================================


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


def test_between_validator_inclusive():
    """Test between validator with inclusive boundaries."""
    config = TyConf(percentage=(int, 50, between(0, 100)))

    config.percentage = 0  # OK (inclusive)
    config.percentage = 100  # OK (inclusive)
    config.percentage = 50  # OK

    with pytest.raises(ValueError, match="must be between 0 and 100"):
        config.percentage = -1

    with pytest.raises(ValueError, match="must be between 0 and 100"):
        config.percentage = 101


def test_between_validator_exclusive():
    """Test between validator with exclusive boundaries."""
    config = TyConf(temperature=(float, 20.5, between(15.0, 25.0, inclusive=False)))

    config.temperature = 20.0  # OK (between)
    config.temperature = 16.0  # OK

    with pytest.raises(ValueError, match="must be between 15.0 and 25.0"):
        config.temperature = 15.0  # Boundary (exclusive)

    with pytest.raises(ValueError, match="must be between 15.0 and 25.0"):
        config.temperature = 25.0  # Boundary (exclusive)


# ============================================================================
# NUMERIC VALIDATORS - Sign
# ============================================================================


def test_positive_validator():
    """Test positive validator."""
    config = TyConf(timeout=(int, 30, positive()))

    config.timeout = 60  # OK
    config.timeout = 1  # OK

    with pytest.raises(ValueError, match="must be positive"):
        config.timeout = 0

    with pytest.raises(ValueError, match="must be positive"):
        config.timeout = -10


def test_negative_validator():
    """Test negative validator."""
    config = TyConf(temperature=(float, -5.0, negative()))

    config.temperature = -10.0  # OK
    config.temperature = -0.1  # OK

    with pytest.raises(ValueError, match="must be negative"):
        config.temperature = 0.0  # Changed: use 0.0 instead of 0

    with pytest.raises(ValueError, match="must be negative"):
        config.temperature = 10.0


def test_non_negative_validator():
    """Test non_negative validator."""
    config = TyConf(count=(int, 0, non_negative()))

    config.count = 0  # OK
    config.count = 100  # OK

    with pytest.raises(ValueError, match="must be non-negative"):
        config.count = -1


def test_non_positive_validator():
    """Test non_positive validator."""
    config = TyConf(debt=(float, -100.0, non_positive()))

    config.debt = 0.0  # Changed: use 0.0 instead of 0
    config.debt = -50.0  # OK

    with pytest.raises(ValueError, match="must be non-positive"):
        config.debt = 10.0


# ============================================================================
# NUMERIC VALIDATORS - Divisibility and parity
# ============================================================================


def test_divisible_by_validator():
    """Test divisible_by validator."""
    config = TyConf(port=(int, 8080, divisible_by(10)))

    config.port = 8080  # OK (divisible by 10)
    config.port = 9000  # OK

    with pytest.raises(ValueError, match="must be divisible by 10"):
        config.port = 8081


def test_is_even_validator():
    """Test is_even validator."""
    config = TyConf(threads=(int, 4, is_even()))

    config.threads = 8  # OK
    config.threads = 2  # OK

    with pytest.raises(ValueError, match="must be even"):
        config.threads = 5


def test_is_odd_validator():
    """Test is_odd validator."""
    config = TyConf(retries=(int, 3, is_odd()))

    config.retries = 5  # OK
    config.retries = 1  # OK

    with pytest.raises(ValueError, match="must be odd"):
        config.retries = 4


# ============================================================================
# COLLECTION VALIDATORS
# ============================================================================


def test_non_empty_validator():
    """Test non_empty validator."""
    config = TyConf(
        tags=(list, ["python"], non_empty()),
        name=(str, "app", non_empty()),
    )

    config.tags = ["python", "config"]  # OK
    config.name = "myapp"  # OK

    with pytest.raises(ValueError, match="must not be empty"):
        config.tags = []

    with pytest.raises(ValueError, match="must not be empty"):
        config.name = ""


def test_unique_items_validator():
    """Test unique_items validator."""
    config = TyConf(tags=(list, ["a", "b"], unique_items()))

    config.tags = ["x", "y", "z"]  # OK

    with pytest.raises(ValueError, match="all items must be unique"):
        config.tags = ["x", "y", "x"]  # Duplicate 'x'


def test_has_items_validator():
    """Test has_items validator."""
    config = TyConf(features=(list, ["api", "web"], has_items("api")))

    config.features = ["api", "web", "cli"]  # OK (contains 'api')

    with pytest.raises(ValueError, match="must contain items"):
        config.features = ["web", "cli"]  # Missing 'api'


def test_has_items_multiple():
    """Test has_items validator with multiple required items."""
    config = TyConf(features=(list, ["api", "web", "db"], has_items("api", "db")))

    config.features = ["api", "web", "db", "cache"]  # OK

    with pytest.raises(ValueError, match="must contain items"):
        config.features = ["api", "web"]  # Missing 'db'


def test_min_items_validator():
    """Test min_items validator."""
    config = TyConf(servers=(list, ["srv1", "srv2"], min_items(2)))

    config.servers = ["srv1", "srv2"]  # OK (exactly 2)
    config.servers = ["srv1", "srv2", "srv3"]  # OK (more than 2)

    with pytest.raises(ValueError, match="must have at least 2 items"):
        config.servers = ["srv1"]


def test_max_items_validator():
    """Test max_items validator."""
    config = TyConf(tags=(list, ["a", "b"], max_items(5)))

    config.tags = ["a", "b", "c"]  # OK (less than 5)
    config.tags = ["a", "b", "c", "d", "e"]  # OK (exactly 5)

    with pytest.raises(ValueError, match="must have at most 5 items"):
        config.tags = ["a", "b", "c", "d", "e", "f"]


# ============================================================================
# DICTIONARY VALIDATORS
# ============================================================================


def test_has_keys_validator():
    """Test has_keys validator."""
    config = TyConf(db_config=(dict, {"host": "localhost", "port": 5432}, has_keys("host", "port")))

    config.db_config = {"host": "localhost", "port": 5432, "user": "admin"}  # OK

    with pytest.raises(ValueError, match="must contain keys"):
        config.db_config = {"host": "localhost"}  # Missing 'port'


def test_keys_in_validator():
    """Test keys_in validator."""
    config = TyConf(options=(dict, {"debug": True}, keys_in("debug", "verbose", "log_level")))

    config.options = {"debug": True, "verbose": False}  # OK

    with pytest.raises(ValueError, match="invalid keys"):
        config.options = {"debug": True, "invalid_key": "value"}


# ============================================================================
# URL VALIDATORS
# ============================================================================


def test_url_scheme_validator():
    """Test url_scheme validator."""
    config = TyConf(api_url=(str, "https://api.example.com", url_scheme("https")))

    config.api_url = "https://secure.com"  # OK

    with pytest.raises(ValueError, match="URL scheme must be one of"):
        config.api_url = "http://insecure.com"


def test_url_scheme_multiple():
    """Test url_scheme validator with multiple allowed schemes."""
    config = TyConf(url=(str, "https://example.com", url_scheme("http", "https", "ftp")))

    config.url = "https://example.com"  # OK
    config.url = "http://example.com"  # OK
    config.url = "ftp://files.example.com"  # OK

    with pytest.raises(ValueError, match="URL scheme must be one of"):
        config.url = "ssh://server.com"


def test_valid_url_validator():
    """Test valid_url validator."""
    config = TyConf(website=(str, "https://example.com", valid_url()))

    config.website = "https://example.com"  # OK
    config.website = "http://test.org"  # OK
    config.website = "ftp://files.com"  # OK

    with pytest.raises(ValueError, match="must be a valid URL"):
        config.website = "not-a-url"

    with pytest.raises(ValueError, match="must be a valid URL"):
        config.website = "example.com"  # Missing scheme


# ============================================================================
# PATH VALIDATORS
# ============================================================================


def test_path_exists_validator(tmp_path):
    """Test path_exists validator."""
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    config = TyConf(config_file=(str, str(test_file), path_exists()))

    # Valid path
    assert config.config_file == str(test_file)

    # Invalid path
    with pytest.raises(ValueError, match="path does not exist"):
        config.config_file = "/nonexistent/path.txt"


def test_is_file_validator(tmp_path):
    """Test is_file validator."""
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    config = TyConf(config_file=(str, str(test_file), is_file()))

    assert config.config_file == str(test_file)

    # Try to set to a directory
    with pytest.raises(ValueError, match="not a file"):
        config.config_file = str(tmp_path)


def test_is_directory_validator(tmp_path):
    """Test is_directory validator."""
    config = TyConf(data_dir=(str, str(tmp_path), is_directory()))

    assert config.data_dir == str(tmp_path)

    # Try to set to a file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    with pytest.raises(ValueError, match="not a directory"):
        config.data_dir = str(test_file)


def test_is_absolute_path_validator():
    """Test is_absolute_path validator."""
    config = TyConf(install_dir=(str, "/opt/app", is_absolute_path()))

    config.install_dir = "/usr/local/app"  # OK

    with pytest.raises(ValueError, match="path must be absolute"):
        config.install_dir = "relative/path"


def test_is_relative_path_validator():
    """Test is_relative_path validator."""
    config = TyConf(config_path=(str, "config/app.conf", is_relative_path()))

    config.config_path = "data/file.txt"  # OK

    with pytest.raises(ValueError, match="path must be relative"):
        config.config_path = "/etc/file.txt"


def test_file_extension_validator():
    """Test file_extension validator."""
    config = TyConf(config_file=(str, "app.json", file_extension(".json", ".yaml")))

    config.config_file = "settings.yaml"  # OK
    config.config_file = "config.json"  # OK

    with pytest.raises(ValueError, match="file extension must be one of"):
        config.config_file = "data.xml"


def test_file_extension_without_dot():
    """Test file_extension validator with extensions without dot."""
    config = TyConf(image=(str, "photo.jpg", file_extension("jpg", "png", "gif")))

    config.image = "photo.jpg"  # OK
    config.image = "icon.png"  # OK

    with pytest.raises(ValueError, match="file extension must be one of"):
        config.image = "document.pdf"


# ============================================================================
# CUSTOM AND COMPLEX VALIDATORS
# ============================================================================


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

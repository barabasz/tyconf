"""Tests for TyConf serialization functionality."""

import json
import os

import pytest

from tyconf import TyConf

# Handle optional tomli_w dependency
try:
    import tomli_w
    HAS_TOML_WRITE = True
except ImportError:
    HAS_TOML_WRITE = False
    tomli_w = None  # Define for later use


# ============================================================================
# JSON SERIALIZATION TESTS
# ============================================================================


def test_to_dict_values_only():
    """Test to_dict with values_only=True."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, True))

    result = config.to_dict(values_only=True)

    assert result == {"host": "localhost", "port": 8080, "debug": True}
    assert "_tyconf_version" not in result
    assert "properties" not in result


def test_to_dict_full_metadata():
    """Test to_dict with full metadata."""
    config = TyConf(host=(str, "localhost"), VERSION=(str, "1.0.0", True))

    result = config.to_dict(values_only=False)

    assert "_tyconf_version" in result
    assert "properties" in result
    assert "host" in result["properties"]
    assert result["properties"]["host"]["type"] == "str"
    assert result["properties"]["host"]["value"] == "localhost"
    assert result["properties"]["VERSION"]["readonly"] is True


def test_to_json_string():
    """Test to_json returns string."""
    config = TyConf(host=(str, "localhost"))

    json_str = config.to_json()

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert "properties" in data


def test_to_json_file(tmp_path):
    """Test to_json saves to file."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080))

    file_path = tmp_path / "config.json"
    result = config.to_json(str(file_path))

    assert result is None  # Returns None when saving to file
    assert file_path.exists()

    with open(file_path) as f:
        data = json.load(f)

    assert "properties" in data


def test_from_json_metadata_format():
    """Test from_json with full metadata."""
    json_data = """
    {
        "_tyconf_version": "1.2.0",
        "properties": {
            "host": {
                "type": "str",
                "value": "localhost",
                "default": "localhost",
                "readonly": false
            },
            "port": {
                "type": "int",
                "value": 8080,
                "default": 8080,
                "readonly": false
            }
        }
    }
    """

    config = TyConf.from_json(json_data)

    assert config.host == "localhost"
    assert config.port == 8080


def test_from_json_values_only_with_schema():
    """Test from_json with values-only format."""
    json_data = '{"host": "localhost", "port": 8080}'

    schema = {"host": (str, ""), "port": (int, 0)}

    config = TyConf.from_json(json_data, schema=schema)

    assert config.host == "localhost"
    assert config.port == 8080


def test_from_json_values_only_without_schema():
    """Test from_json fails without schema for values-only."""
    json_data = '{"host": "localhost"}'

    with pytest.raises(ValueError, match="Schema required"):
        TyConf.from_json(json_data)


def test_from_json_file(tmp_path):
    """Test from_json loads from file."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080))

    file_path = tmp_path / "config.json"
    config.to_json(str(file_path))

    loaded = TyConf.from_json(str(file_path))

    assert loaded.host == "localhost"
    assert loaded.port == 8080


def test_load_json_merge():
    """Test load_json merges into existing config."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, False))

    json_data = '{"port": 3000, "debug": true}'
    config.load_json(json_data)

    assert config.host == "localhost"  # Unchanged
    assert config.port == 3000  # Updated
    assert config.debug is True  # Updated


def test_roundtrip_json():
    """Test JSON roundtrip preserves values."""
    original = TyConf(
        host=(str, "localhost"), port=(int, 8080), debug=(bool, True), VERSION=(str, "1.0.0", True)
    )

    # Modify some values
    original.host = "0.0.0.0"
    original.port = 3000
    original.debug = False

    # Export and import
    json_str = original.to_json()
    loaded = TyConf.from_json(json_str)

    # Check values
    assert loaded.host == "0.0.0.0"
    assert loaded.port == 3000
    assert loaded.debug is False
    assert loaded.VERSION == "1.0.0"

    # Check readonly preserved
    with pytest.raises(AttributeError, match="read-only"):
        loaded.VERSION = "2.0.0"


# ============================================================================
# TOML SERIALIZATION TESTS
# ============================================================================


def test_from_toml_string():
    """Test from_toml with TOML string (built-in, no dependencies)."""
    toml_data = """
host = "localhost"
port = 8080
debug = true
"""

    schema = {"host": (str, ""), "port": (int, 0), "debug": (bool, False)}

    config = TyConf.from_toml(toml_data, schema=schema)

    assert config.host == "localhost"
    assert config.port == 8080
    assert config.debug is True


def test_from_toml_file(tmp_path):
    """Test from_toml with TOML file (built-in, no dependencies)."""
    # Create TOML file
    toml_file = tmp_path / "config.toml"
    toml_file.write_text(
        """
database = "app.db"
timeout = 30
retry = true
"""
    )

    schema = {"database": (str, ""), "timeout": (int, 0), "retry": (bool, False)}

    config = TyConf.from_toml(str(toml_file), schema=schema)

    assert config.database == "app.db"
    assert config.timeout == 30
    assert config.retry is True


def test_from_toml_with_values_only_format(tmp_path):
    """Test from_toml with simple values-only TOML format."""
    toml_file = tmp_path / "simple.toml"
    toml_file.write_text(
        """
name = "MyApp"
version = "1.0.0"
enabled = true
workers = 4
"""
    )

    schema = {
        "name": (str, ""),
        "version": (str, "0.0.0"),
        "enabled": (bool, False),
        "workers": (int, 1),
    }

    config = TyConf.from_toml(str(toml_file), schema=schema)

    assert config.name == "MyApp"
    assert config.version == "1.0.0"
    assert config.enabled is True
    assert config.workers == 4


def test_to_toml_without_tomli_w():
    """Test that to_toml raises helpful error without tomli-w."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080))

    try:
        import tomli_w

        # If tomli-w IS installed, test should work
        result = config.to_toml(values_only=True)
        assert isinstance(result, str)
        assert 'host = "localhost"' in result
    except ImportError:
        # If tomli-w NOT installed, should raise ImportError
        with pytest.raises(ImportError, match="tomli-w"):
            config.to_toml(values_only=True)


@pytest.mark.skipif(not HAS_TOML_WRITE, reason="tomli-w not installed")
def test_to_toml_values_only_with_tomli_w():
    """Test to_toml values_only format (requires tomli-w)."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, True))

    toml_str = config.to_toml(values_only=True)

    assert isinstance(toml_str, str)
    assert 'host = "localhost"' in toml_str
    assert "port = 8080" in toml_str
    assert "debug = true" in toml_str


@pytest.mark.skipif(not HAS_TOML_WRITE, reason="tomli-w not installed")
def test_roundtrip_toml_with_tomli_w(tmp_path):
    """Test TOML roundtrip (requires tomli-w)."""
    original = TyConf(database=(str, "app.db"), timeout=(int, 30), retry=(bool, True))

    # Export to file
    file_path = tmp_path / "config.toml"
    original.to_toml(str(file_path), values_only=True)

    assert file_path.exists()

    # Import from file
    schema = {"database": (str, ""), "timeout": (int, 0), "retry": (bool, False)}
    loaded = TyConf.from_toml(str(file_path), schema=schema)

    assert loaded.database == "app.db"
    assert loaded.timeout == 30
    assert loaded.retry is True


# ============================================================================
# ENVIRONMENT VARIABLE TESTS
# ============================================================================


def test_from_env_basic():
    """Test from_env loads environment variables."""
    os.environ["APP_HOST"] = "localhost"
    os.environ["APP_PORT"] = "8080"
    os.environ["APP_DEBUG"] = "true"

    try:
        config = TyConf.from_env(
            "APP_", schema={"host": (str, ""), "port": (int, 0), "debug": (bool, False)}
        )

        assert config.host == "localhost"
        assert config.port == 8080
        assert config.debug is True
    finally:
        del os.environ["APP_HOST"]
        del os.environ["APP_PORT"]
        del os.environ["APP_DEBUG"]


def test_from_env_type_conversion():
    """Test from_env converts types correctly."""
    os.environ["TEST_INT"] = "42"
    os.environ["TEST_FLOAT"] = "3.14"
    os.environ["TEST_BOOL_TRUE"] = "true"
    os.environ["TEST_BOOL_FALSE"] = "false"

    try:
        config = TyConf.from_env(
            "TEST_",
            schema={
                "int": (int, 0),
                "float": (float, 0.0),
                "bool_true": (bool, False),
                "bool_false": (bool, True),
            },
        )

        assert config.int == 42
        assert config.float == 3.14
        assert config.bool_true is True
        assert config.bool_false is False
    finally:
        del os.environ["TEST_INT"]
        del os.environ["TEST_FLOAT"]
        del os.environ["TEST_BOOL_TRUE"]
        del os.environ["TEST_BOOL_FALSE"]


def test_from_env_bool_variations():
    """Test from_env handles various bool formats."""
    test_cases = [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("off", False),
    ]

    for env_value, expected in test_cases:
        os.environ["TEST_BOOL"] = env_value

        try:
            config = TyConf.from_env("TEST_", schema={"bool": (bool, False)})
            assert config.bool is expected, f"Failed for {env_value}"
        finally:
            del os.environ["TEST_BOOL"]


def test_from_env_defaults():
    """Test from_env uses defaults for missing vars."""
    # Don't set any environment variables

    config = TyConf.from_env("MISSING_", schema={"host": (str, "localhost"), "port": (int, 8080)})

    assert config.host == "localhost"
    assert config.port == 8080


def test_load_env_merge():
    """Test load_env merges into existing config."""
    config = TyConf(host=(str, "localhost"), port=(int, 8080))

    os.environ["APP_PORT"] = "3000"

    try:
        config.load_env("APP_")

        assert config.host == "localhost"  # Unchanged
        assert config.port == 3000  # Updated
    finally:
        del os.environ["APP_PORT"]


def test_from_env_case_insensitive():
    """Test from_env case insensitive matching."""
    os.environ["app_host"] = "localhost"  # lowercase

    try:
        config = TyConf.from_env("APP_", schema={"host": (str, "")})

        assert config.host == "localhost"
    finally:
        del os.environ["app_host"]


# ============================================================================
# MIXED SOURCES TEST
# ============================================================================


def test_mixed_sources(tmp_path):
    """Test loading from multiple sources."""
    # 1. Start with defaults
    config = TyConf(
        host=(str, "localhost"), port=(int, 8080), debug=(bool, False), workers=(int, 4)
    )

    # 2. Load from JSON
    json_file = tmp_path / "config.json"
    with open(json_file, "w") as f:
        json.dump({"host": "0.0.0.0", "workers": 8}, f)

    config.load_json(str(json_file))
    assert config.host == "0.0.0.0"
    assert config.workers == 8
    assert config.port == 8080  # Unchanged

    # 3. Override from environment
    os.environ["APP_PORT"] = "3000"
    os.environ["APP_DEBUG"] = "true"

    try:
        config.load_env("APP_")

        assert config.host == "0.0.0.0"  # From JSON
        assert config.workers == 8  # From JSON
        assert config.port == 3000  # From ENV
        assert config.debug is True  # From ENV
    finally:
        del os.environ["APP_PORT"]
        del os.environ["APP_DEBUG"]


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_from_json_invalid_json():
    """Test from_json handles invalid JSON."""
    with pytest.raises(json.JSONDecodeError):
        TyConf.from_json("invalid json{")


def test_from_env_type_conversion_error():
    """Test from_env handles conversion errors."""
    os.environ["TEST_PORT"] = "not_a_number"

    try:
        with pytest.raises(ValueError, match="Cannot convert"):
            TyConf.from_env("TEST_", schema={"port": (int, 0)})
    finally:
        del os.environ["TEST_PORT"]


def test_load_json_nonexistent_file():
    """Test load_json with non-existent file."""
    config = TyConf(host=(str, "localhost"))

    with pytest.raises(FileNotFoundError):
        config.load_json("/nonexistent/file.json")

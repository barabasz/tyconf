"""Tests for TyConf core functionality."""

import pytest
from typing import Optional, Union
from tyconf import TyConf


def test_create_empty():
    """Test creating empty TyConf."""
    cfg = TyConf()
    assert len(cfg) == 0


def test_create_with_properties():
    """Test creating TyConf with initial properties."""
    cfg = TyConf(name=(str, "test"), port=(int, 8080), debug=(bool, True))
    assert cfg.name == "test"
    assert cfg.port == 8080
    assert cfg.debug is True


def test_add_property():
    """Test adding properties."""
    cfg = TyConf()
    cfg.add("host", str, "localhost")
    assert cfg.host == "localhost"


def test_readonly_property():
    """Test read-only properties."""
    cfg = TyConf(VERSION=(str, "1.0.0", True))

    # Can read
    assert cfg.VERSION == "1.0.0"

    # Cannot modify
    with pytest.raises(AttributeError, match="read-only"):
        cfg.VERSION = "2.0.0"


def test_freeze_unfreeze():
    """Test freeze/unfreeze functionality."""
    cfg = TyConf(debug=(bool, True))

    # Can modify when unfrozen
    cfg.debug = False
    assert cfg.debug is False

    # Freeze
    cfg.freeze()
    assert cfg.frozen is True

    # Cannot modify when frozen
    with pytest.raises(AttributeError, match="frozen"):
        cfg.debug = True

    # Unfreeze
    cfg.unfreeze()
    assert cfg.frozen is False
    cfg.debug = True
    assert cfg.debug is True


def test_type_validation():
    """Test type validation."""
    cfg = TyConf(port=(int, 8080))

    # Valid type
    cfg.port = 3000
    assert cfg.port == 3000

    # Invalid type
    with pytest.raises(TypeError):
        cfg.port = "invalid"


def test_optional_type():
    """Test Optional type support."""
    cfg = TyConf(api_key=(Optional[str], None))

    # None is valid
    assert cfg.api_key is None

    # String is valid
    cfg.api_key = "secret"
    assert cfg.api_key == "secret"

    # Back to None
    cfg.api_key = None
    assert cfg.api_key is None


def test_union_type():
    """Test Union type support."""
    cfg = TyConf(port=(Union[int, str], 8080))

    # Int is valid
    cfg.port = 3000
    assert cfg.port == 3000

    # String is valid
    cfg.port = "auto"
    assert cfg.port == "auto"

    # Float is invalid
    with pytest.raises(TypeError):
        cfg.port = 3.14


def test_dict_interface():
    """Test dict-like interface."""
    cfg = TyConf(host=(str, "localhost"))

    # Get
    assert cfg["host"] == "localhost"

    # Set
    cfg["host"] = "0.0.0.0"
    assert cfg["host"] == "0.0.0.0"

    # Contains
    assert "host" in cfg
    assert "missing" not in cfg

    # Delete
    del cfg["host"]
    assert "host" not in cfg


def test_copy():
    """Test copy method."""
    cfg = TyConf(debug=(bool, True))
    cfg.freeze()

    copy = cfg.copy()

    # Copy is unfrozen
    assert copy.frozen is False

    # Copy has same values
    assert copy.debug is True

    # Modifying copy doesn't affect original
    copy.debug = False
    assert cfg.debug is True


def test_reset():
    """Test reset method."""
    cfg = TyConf(VERSION=(str, "1.0", True), debug=(bool, False))

    cfg.debug = True
    cfg.reset()

    # Mutable property reset
    assert cfg.debug is False

    # Read-only unchanged
    assert cfg.VERSION == "1.0"


def test_iteration():
    """Test iteration over properties."""
    cfg = TyConf(a=(int, 1), b=(int, 2), c=(int, 3))

    keys = list(cfg.keys())
    assert "a" in keys
    assert "b" in keys
    assert "c" in keys

    values = list(cfg.values())
    assert 1 in values
    assert 2 in values
    assert 3 in values


def test_property_info():
    """Test get_property_info."""
    cfg = TyConf(VERSION=(str, "1.0", True))

    info = cfg.get_property_info("VERSION")
    assert info.name == "VERSION"
    assert info.prop_type == str
    assert info.default_value == "1.0"
    assert info.readonly is True


def test_unhashable():
    """Test that TyConf is unhashable."""
    cfg = TyConf(debug=(bool, True))

    with pytest.raises(TypeError, match="unhashable"):
        hash(cfg)

def test_validate_generic_list():
    """Test validation of generic list types."""
    cfg = TyConf(tags=(list[str], []))
    
    # Should accept lists
    cfg.tags = ["a", "b", "c"]
    assert cfg.tags == ["a", "b", "c"]
    
    # Should reject non-lists
    with pytest.raises(TypeError):
        cfg.tags = "not a list"


def test_validate_generic_dict():
    """Test validation of generic dict types."""
    cfg = TyConf(mapping=(dict[str, int], {}))
    
    # Should accept dicts
    cfg.mapping = {"x": 1, "y": 2}
    assert cfg.mapping == {"x": 1, "y": 2}
    
    # Should reject non-dicts
    with pytest.raises(TypeError):
        cfg.mapping = "not a dict"


def test_union_with_generics():
    """Test Union containing generic types."""
    cfg = TyConf(
        data=(Union[list[int], str], [])
    )
    
    # List should work
    cfg.data = [1, 2, 3]
    assert cfg.data == [1, 2, 3]
    
    # String should work
    cfg.data = "text"
    assert cfg.data == "text"
    
    # Other types should fail
    with pytest.raises(TypeError):
        cfg.data = 123


def test_copy_preserves_original_defaults():
    """Test that copy() preserves original default values."""
    cfg = TyConf(
        port=(int, 8080),
        debug=(bool, False)
    )
    
    # Modify values
    cfg.port = 3000
    cfg.debug = True
    
    # Create copy
    copy = cfg.copy()
    
    # Copy has current values
    assert copy.port == 3000
    assert copy.debug is True
    
    # Reset should restore ORIGINAL defaults, not copied values
    copy.reset()
    assert copy.port == 8080  # Back to original default
    assert copy.debug is False  # Back to original default


def test_copy_independence():
    """Test that copy is independent from original."""
    original = TyConf(value=(int, 100))
    copy = original.copy()
    
    # Modify copy
    copy.value = 200
    
    # Original unchanged
    assert original.value == 100
    
    # Modify original
    original.value = 300
    
    # Copy unchanged
    assert copy.value == 200


def test_copy_readonly_properties():
    """Test that readonly properties are copied correctly."""
    cfg = TyConf(
        VERSION=(str, "1.0.0", True),
        debug=(bool, False)
    )
    
    copy = cfg.copy()
    
    # Readonly flag preserved
    assert copy.get_property_info('VERSION').readonly is True
    
    # Value preserved
    assert copy.VERSION == "1.0.0"
    
    # Still readonly
    with pytest.raises(AttributeError, match="read-only"):
        copy.VERSION = "2.0.0"

def test_property_definition_validation():
    """Test validation of property definitions in constructor."""
    
    # Should raise TypeError for non-tuple values
    with pytest.raises(TypeError, match="expected tuple"):
        TyConf(debug=True)
    
    with pytest.raises(TypeError, match="expected tuple"):
        TyConf(host="localhost")
    
    with pytest.raises(TypeError, match="expected tuple"):
        TyConf(port=8080)
    
    # Should raise ValueError for wrong tuple length
    with pytest.raises(ValueError, match="expected tuple of 2 or 3 elements"):
        TyConf(port=(int,))
    
    with pytest.raises(ValueError, match="expected tuple of 2 or 3 elements"):
        TyConf(debug=(bool, True, False, "extra"))


def test_property_definition_error_messages():
    """Test that error messages are helpful."""
    
    # Check error message includes property name
    with pytest.raises(TypeError, match="Property 'debug'"):
        TyConf(debug=True)
    
    # Check error message includes type
    with pytest.raises(TypeError, match="got bool"):
        TyConf(debug=True)
    
    # Check error message includes example
    with pytest.raises(TypeError, match="Example:"):
        TyConf(host="localhost")
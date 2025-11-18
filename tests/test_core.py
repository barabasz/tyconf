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


def test_add_property_to_frozen():
    """Test that adding property to frozen TyConf raises error."""
    cfg = TyConf()
    cfg.freeze()

    with pytest.raises(AttributeError, match="Cannot add properties to frozen"):
        cfg.add("new_prop", str, "value")


def test_add_duplicate_property():
    """Test that adding duplicate property raises error."""
    cfg = TyConf(host=(str, "localhost"))

    with pytest.raises(AttributeError, match="already exists"):
        cfg.add("host", str, "other")


def test_readonly_property():
    """Test read-only properties."""
    cfg = TyConf(VERSION=(str, "1.0.0", True))

    # Can read
    assert cfg.VERSION == "1.0.0"

    # Cannot modify
    with pytest.raises(AttributeError, match="read-only"):
        cfg.VERSION = "2.0.0"


def test_readonly_property_via_dict_access():
    """Test read-only properties via dict-style access."""
    cfg = TyConf(VERSION=(str, "1.0.0", True))

    # Can read
    assert cfg["VERSION"] == "1.0.0"

    # Cannot modify
    with pytest.raises(AttributeError, match="read-only"):
        cfg["VERSION"] = "2.0.0"


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


def test_freeze_prevents_remove():
    """Test that frozen TyConf prevents property removal."""
    cfg = TyConf(temp=(str, "value"))
    cfg.freeze()

    with pytest.raises(AttributeError, match="Cannot delete properties from frozen"):
        cfg.remove("temp")


def test_freeze_prevents_dict_delete():
    """Test that frozen TyConf prevents dict-style deletion."""
    cfg = TyConf(temp=(str, "value"))
    cfg.freeze()

    with pytest.raises(AttributeError, match="Cannot delete properties from frozen"):
        del cfg["temp"]


def test_freeze_prevents_reset():
    """Test that frozen TyConf cannot be reset."""
    cfg = TyConf(debug=(bool, False))
    cfg.debug = True
    cfg.freeze()

    with pytest.raises(AttributeError, match="Cannot reset frozen"):
        cfg.reset()


def test_type_validation():
    """Test type validation."""
    cfg = TyConf(port=(int, 8080))

    # Valid type
    cfg.port = 3000
    assert cfg.port == 3000

    # Invalid type
    with pytest.raises(TypeError):
        cfg.port = "invalid"


def test_type_validation_on_init():
    """Test type validation during initialization."""
    # Should validate default value
    with pytest.raises(TypeError, match="expected int"):
        TyConf(port=(int, "not_an_int"))


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


def test_optional_type_invalid():
    """Test Optional type rejects wrong types."""
    cfg = TyConf(api_key=(Optional[str], None))

    with pytest.raises(TypeError):
        cfg.api_key = 123


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


def test_dict_getitem_missing():
    """Test that accessing missing property via dict raises KeyError."""
    cfg = TyConf()

    with pytest.raises(KeyError):
        _ = cfg["missing"]


def test_dict_setitem_missing():
    """Test that setting missing property via dict raises KeyError."""
    cfg = TyConf()

    with pytest.raises(KeyError):
        cfg["missing"] = "value"


def test_attribute_access_missing():
    """Test that accessing missing property via attribute raises AttributeError."""
    cfg = TyConf()

    with pytest.raises(AttributeError, match="has no property"):
        _ = cfg.missing


def test_attribute_setattr_missing():
    """Test that setting missing property via attribute raises AttributeError."""
    cfg = TyConf()

    with pytest.raises(AttributeError, match="has no property"):
        cfg.missing = "value"


def test_remove_method():
    """Test remove() method."""
    cfg = TyConf(temp=(str, "value"))

    assert "temp" in cfg
    cfg.remove("temp")
    assert "temp" not in cfg


def test_remove_missing():
    """Test removing non-existent property."""
    cfg = TyConf()

    with pytest.raises(AttributeError, match="does not exist"):
        cfg.remove("missing")


def test_remove_readonly():
    """Test that removing read-only property raises error."""
    cfg = TyConf(VERSION=(str, "1.0", True))

    with pytest.raises(AttributeError, match="read-only"):
        cfg.remove("VERSION")


def test_update_single():
    """Test update() with single property."""
    cfg = TyConf(debug=(bool, False))

    cfg.update(debug=True)
    assert cfg.debug is True


def test_update_multiple():
    """Test update() with multiple properties."""
    cfg = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, False))

    cfg.update(host="0.0.0.0", port=3000, debug=True)

    assert cfg.host == "0.0.0.0"
    assert cfg.port == 3000
    assert cfg.debug is True


def test_update_readonly():
    """Test that update() respects read-only properties."""
    cfg = TyConf(VERSION=(str, "1.0", True))

    with pytest.raises(AttributeError, match="read-only"):
        cfg.update(VERSION="2.0")


def test_update_with_type_error():
    """Test that update() validates types."""
    cfg = TyConf(port=(int, 8080))

    with pytest.raises(TypeError):
        cfg.update(port="invalid")


def test_update_missing_property():
    """Test that update() raises error for non-existent properties."""
    cfg = TyConf(debug=(bool, True))

    with pytest.raises(AttributeError, match="has no property"):
        cfg.update(missing="value")


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


def test_copy_preserves_original_defaults():
    """Test that copy() preserves original default values."""
    cfg = TyConf(port=(int, 8080), debug=(bool, False))

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
    cfg = TyConf(VERSION=(str, "1.0.0", True), debug=(bool, False))

    copy = cfg.copy()

    # Readonly flag preserved
    assert copy.get_property_info("VERSION").readonly is True

    # Value preserved
    assert copy.VERSION == "1.0.0"

    # Still readonly
    with pytest.raises(AttributeError, match="read-only"):
        copy.VERSION = "2.0.0"


def test_copy_empty_config():
    """Test copying empty configuration."""
    cfg = TyConf()
    copy = cfg.copy()

    assert len(copy) == 0
    assert copy.frozen is False


def test_reset():
    """Test reset method."""
    cfg = TyConf(VERSION=(str, "1.0", True), debug=(bool, False))

    cfg.debug = True
    cfg.reset()

    # Mutable property reset
    assert cfg.debug is False

    # Read-only unchanged
    assert cfg.VERSION == "1.0"


def test_reset_multiple_properties():
    """Test reset with multiple properties."""
    cfg = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, False))

    cfg.host = "0.0.0.0"
    cfg.port = 3000
    cfg.debug = True

    cfg.reset()

    assert cfg.host == "localhost"
    assert cfg.port == 8080
    assert cfg.debug is False


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


def test_iteration_empty():
    """Test iteration over empty configuration."""
    cfg = TyConf()

    assert list(cfg.keys()) == []
    assert list(cfg.values()) == []
    assert list(cfg.items()) == []
    assert list(cfg) == []


def test_items_iteration():
    """Test items() iteration."""
    cfg = TyConf(x=(int, 10), y=(int, 20))

    items = dict(cfg.items())
    assert items == {"x": 10, "y": 20}


def test_for_loop_iteration():
    """Test for loop over TyConf."""
    cfg = TyConf(a=(int, 1), b=(int, 2), c=(int, 3))

    names = []
    for name in cfg:
        names.append(name)

    assert set(names) == {"a", "b", "c"}


def test_list_properties():
    """Test list_properties() method."""
    cfg = TyConf(host=(str, "localhost"), port=(int, 8080))

    props = cfg.list_properties()
    assert isinstance(props, list)
    assert set(props) == {"host", "port"}


def test_list_properties_empty():
    """Test list_properties() on empty config."""
    cfg = TyConf()
    assert cfg.list_properties() == []


def test_get_method():
    """Test get() method."""
    cfg = TyConf(debug=(bool, True))

    assert cfg.get("debug") is True
    assert cfg.get("missing", "default") == "default"
    assert cfg.get("missing") is None


def test_get_method_with_none_default():
    """Test get() with explicit None default."""
    cfg = TyConf()
    assert cfg.get("missing", None) is None


def test_property_info():
    """Test get_property_info."""
    cfg = TyConf(VERSION=(str, "1.0", True))

    info = cfg.get_property_info("VERSION")
    assert info.name == "VERSION"
    assert info.prop_type == str
    assert info.default_value == "1.0"
    assert info.readonly is True


def test_property_info_mutable():
    """Test get_property_info for mutable property."""
    cfg = TyConf(debug=(bool, False))

    info = cfg.get_property_info("debug")
    assert info.name == "debug"
    assert info.prop_type == bool
    assert info.default_value is False
    assert info.readonly is False


def test_property_info_missing():
    """Test get_property_info for non-existent property."""
    cfg = TyConf()

    with pytest.raises(AttributeError, match="does not exist"):
        cfg.get_property_info("missing")


def test_len():
    """Test __len__ method."""
    cfg = TyConf()
    assert len(cfg) == 0

    cfg.add("a", int, 1)
    assert len(cfg) == 1

    cfg.add("b", int, 2)
    assert len(cfg) == 2

    cfg.remove("a")
    assert len(cfg) == 1


def test_str_representation():
    """Test __str__ method."""
    cfg = TyConf(host=(str, "localhost"), port=(int, 8080))

    s = str(cfg)
    assert "TyConf(" in s
    assert "host" in s
    assert "localhost" in s
    assert "port" in s
    assert "8080" in s


def test_str_representation_empty():
    """Test __str__ for empty config."""
    cfg = TyConf()
    assert str(cfg) == "TyConf()"


def test_repr_representation():
    """Test __repr__ method."""
    cfg = TyConf(a=(int, 1), b=(int, 2))

    r = repr(cfg)
    assert "<TyConf with 2 properties>" == r


def test_repr_representation_empty():
    """Test __repr__ for empty config."""
    cfg = TyConf()
    assert repr(cfg) == "<TyConf with 0 properties>"


def test_unhashable():
    """Test that TyConf is unhashable."""
    cfg = TyConf(debug=(bool, True))

    with pytest.raises(TypeError, match="unhashable"):
        hash(cfg)


def test_show_method(capsys):
    """Test show() method output."""
    cfg = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, True))

    cfg.show()
    captured = capsys.readouterr()

    assert "Configuration properties:" in captured.out
    assert "host" in captured.out
    assert "localhost" in captured.out
    assert "port" in captured.out
    assert "8080" in captured.out
    assert "debug" in captured.out
    assert "True" in captured.out


def test_show_empty(capsys):
    """Test show() on empty configuration."""
    cfg = TyConf()
    cfg.show()

    captured = capsys.readouterr()
    assert "No properties defined" in captured.out


def test_show_long_string(capsys):
    """Test show() with long string values."""
    long_string = "a" * 100
    cfg = TyConf(data=(str, long_string))

    cfg.show()
    captured = capsys.readouterr()

    # Should truncate long strings
    assert "..." in captured.out


def test_show_list(capsys):
    """Test show() with list values."""
    cfg = TyConf(tags=(list, ["a", "b", "c"]))

    cfg.show()
    captured = capsys.readouterr()

    assert "['a', 'b', 'c']" in captured.out


def test_show_large_list(capsys):
    """Test show() with large list (should truncate)."""
    cfg = TyConf(items=(list, list(range(10))))

    cfg.show()
    captured = capsys.readouterr()

    # Should show truncation for large lists
    assert "..." in captured.out


def test_show_dict(capsys):
    """Test show() with dict values."""
    cfg = TyConf(mapping=(dict, {"x": 1, "y": 2}))

    cfg.show()
    captured = capsys.readouterr()

    assert "mapping" in captured.out


def test_show_tuple(capsys):
    """Test show() with tuple values."""
    cfg = TyConf(coords=(tuple, (1.5, 2.5)))

    cfg.show()
    captured = capsys.readouterr()

    assert "(1.5, 2.5)" in captured.out


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


def test_validate_generic_tuple():
    """Test validation of generic tuple types."""
    cfg = TyConf(coords=(tuple[float, float], (0.0, 0.0)))

    cfg.coords = (1.5, 2.5)
    assert cfg.coords == (1.5, 2.5)

    with pytest.raises(TypeError):
        cfg.coords = [1.5, 2.5]  # List not tuple


def test_union_with_generics():
    """Test Union containing generic types."""
    cfg = TyConf(data=(Union[list[int], str], []))

    # List should work
    cfg.data = [1, 2, 3]
    assert cfg.data == [1, 2, 3]

    # String should work
    cfg.data = "text"
    assert cfg.data == "text"

    # Other types should fail
    with pytest.raises(TypeError):
        cfg.data = 123


def test_union_with_none():
    """Test Union with None."""
    cfg = TyConf(value=(Union[int, None], None))

    cfg.value = 42
    assert cfg.value == 42

    cfg.value = None
    assert cfg.value is None


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


def test_property_definition_with_list():
    """Test that list can be used instead of tuple for property definition."""
    cfg = TyConf(debug=[bool, True])
    assert cfg.debug is True


def test_internal_attributes():
    """Test that internal attributes are accessible."""
    cfg = TyConf(debug=(bool, True))

    # Should be able to access internal attributes
    assert isinstance(cfg._properties, dict)
    assert isinstance(cfg._values, dict)
    assert isinstance(cfg._frozen, bool)


def test_multiple_types():
    """Test configuration with various Python types."""
    cfg = TyConf(
        string=(str, "text"),
        integer=(int, 42),
        floating=(float, 3.14),
        boolean=(bool, True),
        listing=(list, [1, 2, 3]),
        dictionary=(dict, {"key": "value"}),
        tupling=(tuple, (1, 2, 3)),
    )

    assert cfg.string == "text"
    assert cfg.integer == 42
    assert cfg.floating == 3.14
    assert cfg.boolean is True
    assert cfg.listing == [1, 2, 3]
    assert cfg.dictionary == {"key": "value"}
    assert cfg.tupling == (1, 2, 3)


def test_empty_collections():
    """Test with empty collections as defaults."""
    cfg = TyConf(empty_list=(list, []), empty_dict=(dict, {}), empty_tuple=(tuple, ()))

    assert cfg.empty_list == []
    assert cfg.empty_dict == {}
    assert cfg.empty_tuple == ()


def test_none_values():
    """Test with None as default value."""
    cfg = TyConf(nullable=(Optional[str], None))

    assert cfg.nullable is None
    assert cfg.get("nullable") is None


def test_boolean_edge_cases():
    """Test boolean property edge cases."""
    cfg = TyConf(flag=(bool, False))

    cfg.flag = True
    assert cfg.flag is True

    cfg.flag = False
    assert cfg.flag is False

    # Should not accept truthy values that aren't bool
    with pytest.raises(TypeError):
        cfg.flag = 1

    with pytest.raises(TypeError):
        cfg.flag = "true"


def test_numeric_types():
    """Test different numeric type validation."""
    cfg = TyConf(integer=(int, 0), floating=(float, 0.0))

    # int accepts int
    cfg.integer = 42

    # int doesn't accept float
    with pytest.raises(TypeError):
        cfg.integer = 3.14

    # float accepts float
    cfg.floating = 3.14

    # float doesn't accept int (strict typing)
    with pytest.raises(TypeError):
        cfg.floating = 42


def test_case_sensitivity():
    """Test that property names are case-sensitive."""
    cfg = TyConf(Host=(str, "localhost"), host=(str, "127.0.0.1"))

    assert cfg.Host == "localhost"
    assert cfg.host == "127.0.0.1"


def test_reserved_property_names():
    """Test that property names starting with '_' are rejected."""
    # Should raise ValueError for names starting with underscore
    with pytest.raises(ValueError, match="reserved"):
        TyConf(_private=(str, "value"))

    with pytest.raises(ValueError, match="reserved"):
        TyConf(_internal=(int, 42))

    # Via add() method
    cfg = TyConf()
    with pytest.raises(ValueError, match="reserved"):
        cfg.add("_new", str, "test")


def test_valid_special_property_names():
    """Test properties with valid special names."""
    cfg = TyConf(
        MAX_VALUE=(int, 100),
        snake_case=(bool, True),
        camelCase=(str, "test"),
        UPPER_CASE=(str, "constant"),
    )

    # All should work
    assert cfg.MAX_VALUE == 100
    assert cfg.snake_case is True
    assert cfg.camelCase == "test"
    assert cfg.UPPER_CASE == "constant"


def test_dict_delitem_missing():
    """Test that deleting missing property via dict raises KeyError."""
    cfg = TyConf()

    # Should raise KeyError, NOT AttributeError
    with pytest.raises(KeyError):
        del cfg["missing"]


def test_add_empty_property_name():
    """Test validation of empty or whitespace-only property names."""
    cfg = TyConf()

    # Test empty string
    with pytest.raises(ValueError, match="cannot be empty"):
        cfg.add("", str, "value")

    # Test whitespace
    with pytest.raises(ValueError, match="cannot be empty"):
        cfg.add("   ", str, "value")

    # Test via constructor (using dict unpacking for invalid identifiers)
    with pytest.raises(ValueError, match="cannot be empty"):
        TyConf(**{"": (str, "value")})


def test_update_empty():
    """Test update() with no arguments does nothing."""
    cfg = TyConf(debug=(bool, False))

    # Should not raise error
    cfg.update()

    # Value should be unchanged
    assert cfg.debug is False

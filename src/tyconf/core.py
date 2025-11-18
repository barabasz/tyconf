"""
TyConf - Core implementation for type-safe configuration management.

This module provides the core TyConf class and PropertyDescriptor for managing
configuration with runtime type validation and value validators.
"""

from typing import Any, Union, Optional, Callable, get_args, get_origin
from dataclasses import dataclass


@dataclass
class PropertyDescriptor:
    """Descriptor for a TyConf property."""

    name: str
    prop_type: type
    default_value: Any
    readonly: bool = False
    validator: Optional[Callable[[Any], Any]] = None


class TyConf:
    """
    Type-safe configuration manager with runtime validation.

    TyConf (Typed Config) provides a robust way to manage application configuration
    with automatic type validation, value validation, read-only properties, and
    freeze/unfreeze capabilities.

    Attributes:
        _properties: Dictionary mapping property names to their descriptors.
        _values: Dictionary storing current property values.
        _frozen: Flag indicating if configuration is frozen (immutable).

    Examples:
        >>> config = TyConf(
        ...     host=(str, "localhost"),
        ...     port=(int, 8080, lambda x: 1024 <= x <= 65535),
        ...     debug=(bool, True)
        ... )
        >>> config.host
        'localhost'
        >>> config.port = 3000
        >>> config.port
        3000
    """

    # Class-level type hints for instance attributes
    _properties: dict[str, PropertyDescriptor]
    _values: dict[str, Any]
    _frozen: bool

    # Constants for display formatting
    _MAX_DISPLAY_WIDTH: int = 80
    _PROPERTY_COL_WIDTH: int = 16
    _VALUE_COL_WIDTH: int = 14
    _TYPE_COL_WIDTH: int = 20
    _MAX_COLLECTION_ITEMS: int = 5
    _MAX_STRING_LENGTH: int = 50

    def __init__(self, **properties):
        """
        Initialize TyConf with properties.

        Args:
            **properties: Keyword arguments where each value is a tuple of:
                         - (type, default_value) - Regular property
                         - (type, default_value, readonly) - Read-only property when readonly=True
                         - (type, default_value, validator) - Property with validator (callable)

        Raises:
            TypeError: If property definition is not a tuple/list or third parameter
                      is neither bool nor callable.
            ValueError: If tuple has wrong number of elements.

        Examples:
            >>> config = TyConf(
            ...     VERSION=(str, "1.0.0", True),  # Read-only
            ...     port=(int, 8080, lambda x: 1024 <= x <= 65535),  # With validator
            ...     debug=(bool, False)  # Regular
            ... )
        """
        # Internal storage
        object.__setattr__(self, "_properties", {})
        object.__setattr__(self, "_values", {})
        object.__setattr__(self, "_frozen", False)

        # Add properties
        for name, prop_def in properties.items():
            # Validate property definition format
            if not isinstance(prop_def, (tuple, list)):
                raise TypeError(
                    f"Property '{name}': expected tuple (type, value) or "
                    f"(type, value, readonly) or (type, value, validator), "
                    f"got {type(prop_def).__name__}. "
                    f"Example: {name}=({type(prop_def).__name__}, {prop_def!r})"
                )

            if len(prop_def) == 2:
                prop_type, default_value = prop_def
                readonly = False
                validator = None
            elif len(prop_def) == 3:
                prop_type, default_value, third_param = prop_def

                # AUTO-DETECT: bool = readonly, callable = validator
                if isinstance(third_param, bool):
                    readonly = third_param
                    validator = None
                elif callable(third_param):
                    readonly = False
                    validator = third_param
                else:
                    raise TypeError(
                        f"Property '{name}': third parameter must be bool (readonly) "
                        f"or callable (validator), got {type(third_param).__name__}"
                    )
            else:
                raise ValueError(
                    f"Property '{name}': expected tuple of 2 or 3 elements, got {len(prop_def)}. "
                    f"Valid formats: ({name}=(type, value)), ({name}=(type, value, readonly)), "
                    f"or ({name}=(type, value, validator))"
                )

            self.add(name, prop_type, default_value, readonly, validator)

    def add(
        self,
        name: str,
        prop_type: type,
        default_value: Any,
        readonly: bool = False,
        validator: Optional[Callable] = None,
    ):
        """
        Add a new property to the TyConf.

        Args:
            name: Property name.
            prop_type: Expected type for the property.
            default_value: Default value for the property.
            readonly: If True, property cannot be modified after creation.
            validator: Optional callable to validate property values.

        Raises:
            AttributeError: If TyConf is frozen or property already exists.
            ValueError: If property name is reserved (starts with '_') or validator fails.
            TypeError: If default_value doesn't match prop_type.

        Examples:
            >>> config = TyConf()
            >>> config.add('host', str, 'localhost')
            >>> config.add('port', int, 8080, validator=lambda x: 1024 <= x <= 65535)
            >>> config.host
            'localhost'
        """
        if self._frozen:
            raise AttributeError("Cannot add properties to frozen TyConf")

        # Validate property name not empty
        if not name or not name.strip():
            raise ValueError("Property name cannot be empty")

        # Validate property name starting with underscore
        if name.startswith("_"):
            raise ValueError(
                f"Property name '{name}' is reserved. "
                f"Names starting with '_' are reserved for internal use. "
                f"Please use a name without leading underscore."
            )

        if name in self._properties:
            raise AttributeError(f"Property '{name}' already exists")

        # Validate default value type
        self._validate_type(name, default_value, prop_type)

        # Validate default value with validator
        if validator is not None:
            self._validate_value(name, default_value, validator)

        # Store property descriptor and value
        self._properties[name] = PropertyDescriptor(
            name=name,
            prop_type=prop_type,
            default_value=default_value,
            readonly=readonly,
            validator=validator,
        )
        self._values[name] = default_value

    def remove(self, name: str):
        """
        Remove a property from the TyConf.

        Args:
            name: Property name to remove.

        Raises:
            AttributeError: If TyConf is frozen, property doesn't exist, or property is read-only.

        Examples:
            >>> config = TyConf(debug=(bool, True))
            >>> config.remove('debug')
            >>> 'debug' in config
            False
        """
        try:
            self._del_property(name)
        except KeyError:
            # Convert KeyError to AttributeError for method-style access
            raise AttributeError(f"Property '{name}' does not exist")

    def update(self, **kwargs):
        """
        Update multiple property values at once.

        Args:
            **kwargs: Property names and their new values.

        Raises:
            AttributeError: If any property is read-only or doesn't exist.
            TypeError: If any value doesn't match its property type.
            ValueError: If any value fails validator.

        Examples:
            >>> config = TyConf(host=(str, "localhost"), port=(int, 8080))
            >>> config.update(host="0.0.0.0", port=3000)
            >>> config.host
            '0.0.0.0'
        """
        for name, value in kwargs.items():
            setattr(self, name, value)

    def copy(self) -> "TyConf":
        """
        Create an unfrozen copy of the TyConf.

        The copy preserves:
        - Original default values (so reset() works correctly)
        - Current property values
        - Property types, readonly flags, and validators

        The copy is always unfrozen, even if the original is frozen.

        Returns:
            A new TyConf instance with the same properties and current values.

        Examples:
            >>> config = TyConf(debug=(bool, True))
            >>> config.debug = False
            >>> config.freeze()
            >>> copy = config.copy()
            >>> copy.frozen
            False
            >>> copy.debug
            False
            >>> copy.reset()  # Returns to original default (True)
            >>> copy.debug
            True
        """
        new_config = TyConf()

        # Copy properties with original defaults and current values
        for name, prop in self._properties.items():
            # Step 1: Add property with ORIGINAL default value
            # This ensures reset() will restore to the original default
            new_config.add(
                name=name,
                prop_type=prop.prop_type,
                default_value=prop.default_value,  # Original default, NOT current value
                readonly=prop.readonly,
                validator=prop.validator,
            )

            # Step 2: Set CURRENT value from source
            # Direct access to _values is intentional here to:
            # - Avoid triggering validation again (already validated)
            # - Bypass readonly checks (we're copying, not modifying)
            new_config._values[name] = self._values[name]

        return new_config

    def reset(self):
        """
        Reset all mutable properties to their default values.

        Read-only properties are not affected.

        Raises:
            AttributeError: If TyConf is frozen.

        Examples:
            >>> config = TyConf(debug=(bool, False))
            >>> config.debug = True
            >>> config.reset()
            >>> config.debug
            False
        """
        if self._frozen:
            raise AttributeError("Cannot reset frozen TyConf")

        for name, prop in self._properties.items():
            if not prop.readonly:
                self._values[name] = prop.default_value

    def freeze(self):
        """
        Freeze the TyConf, preventing all modifications.

        Examples:
            >>> config = TyConf(debug=(bool, True))
            >>> config.freeze()
            >>> config.frozen
            True
        """
        object.__setattr__(self, "_frozen", True)

    def unfreeze(self):
        """
        Unfreeze the TyConf, allowing modifications.

        Examples:
            >>> config = TyConf(debug=(bool, True))
            >>> config.freeze()
            >>> config.unfreeze()
            >>> config.frozen
            False
        """
        object.__setattr__(self, "_frozen", False)

    @property
    def frozen(self) -> bool:
        """Check if TyConf is frozen."""
        return self._frozen

    def show(self):
        """
        Display all properties in a formatted table.

        Examples:
            >>> config = TyConf(host=(str, "localhost"), port=(int, 8080))
            >>> config.show()
            Configuration properties:
            --------------------------------------------
            host             = 'localhost'     str
            port             = 8080            int
            --------------------------------------------
        """
        if not self._properties:
            print("No properties defined")
            return

        print("Configuration properties:")
        print("-" * 44)

        for name in sorted(self._properties.keys()):
            prop = self._properties[name]
            value = self._values[name]
            formatted_value = self._format_value_for_display(value)

            # Format: name = value type
            print(f"{name:<16} = {formatted_value:<14} {prop.prop_type.__name__}")

        print("-" * 44)

    def get_property_info(self, name: str) -> PropertyDescriptor:
        """
        Get descriptor information for a property.

        Args:
            name: Property name.

        Returns:
            PropertyDescriptor with property metadata.

        Raises:
            AttributeError: If property doesn't exist.

        Examples:
            >>> config = TyConf(VERSION=(str, "1.0", True))
            >>> info = config.get_property_info('VERSION')
            >>> info.readonly
            True
        """
        if name not in self._properties:
            raise AttributeError(f"Property '{name}' does not exist")

        return self._properties[name]

    def list_properties(self) -> list:
        """
        Get a list of all property names.

        Returns:
            List of property names.

        Examples:
            >>> config = TyConf(host=(str, "localhost"), port=(int, 8080))
            >>> config.list_properties()
            ['host', 'port']
        """
        return list(self._properties.keys())

    def get(self, name: str, default: Any = None) -> Any:
        """
        Get a property value with optional default.

        Args:
            name: Property name.
            default: Value to return if property doesn't exist.

        Returns:
            Property value or default.

        Examples:
            >>> config = TyConf(debug=(bool, True))
            >>> config.get('debug')
            True
            >>> config.get('missing', 'default')
            'default'
        """
        if name in self._properties:
            return self._values[name]
        return default

    def keys(self):
        """Return an iterator over property names."""
        return iter(self._properties.keys())

    def values(self):
        """Return an iterator over property values."""
        return iter(self._values[name] for name in self._properties.keys())

    def items(self):
        """Return an iterator over (name, value) pairs."""
        return iter((name, self._values[name]) for name in self._properties.keys())

    def _set_property(self, name: str, value: Any) -> None:
        """
        Internal helper to set property value with validation.
        This method contains the shared logic for __setattr__ and __setitem__.

        Args:
            name: Property name.
            value: Value to set.

        Raises:
            AttributeError: If TyConf is frozen or property is read-only.
            KeyError: If property doesn't exist (caller should catch and re-raise appropriately).
            TypeError: If value doesn't match property type.
            ValueError: If value fails validator.
        """
        if self._frozen:
            raise AttributeError("Cannot modify frozen TyConf")

        if name not in self._properties:
            # Caller will convert this to appropriate error type
            # (AttributeError for __setattr__, KeyError for __setitem__)
            raise KeyError(name)

        prop = self._properties[name]

        if prop.readonly:
            raise AttributeError(f"Property '{name}' is read-only")

        # Validate type
        self._validate_type(name, value, prop.prop_type)

        # Validate with validator (if exists)
        if prop.validator is not None:
            self._validate_value(name, value, prop.validator)

        self._values[name] = value

    def _del_property(self, name: str) -> None:
        """
        Internal helper to delete property safely.
        This method contains the shared logic for remove() and __delitem__.

        Args:
            name: Property name to delete.

        Raises:
            AttributeError: If TyConf is frozen or property is read-only.
            KeyError: If property doesn't exist (caller should catch and re-raise appropriately).
        """
        if self._frozen:
            raise AttributeError("Cannot delete properties from frozen TyConf")

        if name not in self._properties:
            # Caller will convert this to appropriate error type
            # (AttributeError for remove(), KeyError for __delitem__)
            raise KeyError(name)

        if self._properties[name].readonly:
            raise AttributeError(f"Cannot delete read-only property '{name}'")

        # Delete from both dictionaries
        del self._properties[name]
        del self._values[name]

    def _validate_type(self, name: str, value: Any, expected_type: type):
        """
        Validate that a value matches the expected type.
        Supports Optional, Union and Generics (e.g. list[str], dict[str, int]).

        Args:
            name: Property name (for error messages).
            value: Value to validate.
            expected_type: Expected type.

        Raises:
            TypeError: If value doesn't match expected_type.
        """
        origin = get_origin(expected_type)

        if origin is Union:
            # Handle Optional[T] (Union[T, None]) and Union types
            args = get_args(expected_type)

            # Check if value matches any of the union types
            if value is None and type(None) in args:
                return

            for arg in args:
                if arg is type(None):
                    continue

                # Extract base type for generics inside Union
                # e.g. Union[list[int], str] -> check against list, not list[int]
                check_type = get_origin(arg) or arg

                try:
                    if isinstance(value, check_type):
                        return
                except TypeError:
                    # Some types from typing module don't work with isinstance
                    pass

            # If we get here, value doesn't match any union type
            type_names = ", ".join(
                getattr(arg, "__name__", str(arg)) for arg in args if arg is not type(None)
            )
            raise TypeError(
                f"Property '{name}': expected one of ({type_names}), got {type(value).__name__}"
            )

        # Handle regular types and generics (e.g. list[str] -> list)
        check_type = origin or expected_type

        if not isinstance(value, check_type):
            # Format type name safely
            expected_name = getattr(expected_type, "__name__", str(expected_type))
            raise TypeError(
                f"Property '{name}': expected {expected_name}, " f"got {type(value).__name__}"
            )

    def _validate_value(self, name: str, value: Any, validator: Callable):
        """
        Validate value using validator function.

        Validator can:
        1. Return True/False
        2. Raise exception with custom message
        3. Return None (treated as success)

        Args:
            name: Property name (for error messages).
            value: Value to validate.
            validator: Validator callable.

        Raises:
            ValueError: If validation fails.
        """
        try:
            result = validator(value)

            # If validator returns bool, check it
            if isinstance(result, bool) and result is False:
                raise ValueError(f"Property '{name}': validation failed for value {value!r}")
            # If returns None or True, it's OK

        except Exception as e:
            # Re-raise with property context if not already a ValueError
            if not isinstance(e, ValueError):
                raise ValueError(f"Property '{name}': validation error: {str(e)}") from e
            raise

    def _format_value_for_display(self, value: Any) -> str:
        """
        Format a value for display in the show() method.

        Args:
            value: Value to format.

        Returns:
            Formatted string representation.
        """
        if isinstance(value, str):
            # Truncate long strings
            if len(value) > self._MAX_STRING_LENGTH:
                truncated = value[: self._MAX_STRING_LENGTH - 3] + "..."
                return f"'{truncated}'"
            return f"'{value}'"

        elif isinstance(value, (list, tuple)):
            # Format collections
            if len(value) > self._MAX_COLLECTION_ITEMS:
                items = [
                    self._format_collection_item(v) for v in value[: self._MAX_COLLECTION_ITEMS]
                ]
                items_str = ", ".join(items)
                if isinstance(value, list):
                    return f"[{items_str}, ...]"
                else:
                    return f"({items_str}, ...)"
            else:
                items = [self._format_collection_item(v) for v in value]
                items_str = ", ".join(items)
                if isinstance(value, list):
                    return f"[{items_str}]"
                else:
                    return f"({items_str})"

        elif isinstance(value, dict):
            # Format dictionaries
            if len(value) > self._MAX_COLLECTION_ITEMS:
                return "{...}"
            return str(value)

        else:
            return str(value)

    def _format_collection_item(self, item: Any) -> str:
        """
        Format an item within a collection.

        Args:
            item: Collection item to format.

        Returns:
            Formatted string representation.
        """
        if isinstance(item, str):
            return f"'{item}'"
        return str(item)

    # Special methods for dict-like interface

    def __contains__(self, name: str) -> bool:
        """Check if a property exists."""
        return name in self._properties

    def __getattr__(self, name: str) -> Any:
        """Get property value via attribute access."""
        if name.startswith("_"):
            # Allow access to internal attributes
            return object.__getattribute__(self, name)

        if name in self._properties:
            return self._values[name]

        raise AttributeError(f"TyConf has no property '{name}'")

    def __setattr__(self, name: str, value: Any):
        """Set property value via attribute access."""
        if name.startswith("_"):
            # Allow setting internal attributes during initialization
            object.__setattr__(self, name, value)
            return

        try:
            self._set_property(name, value)
        except KeyError:
            # Convert KeyError to AttributeError for attribute access
            raise AttributeError(f"TyConf has no property '{name}'")

    def __len__(self) -> int:
        """Return number of properties."""
        return len(self._properties)

    def __iter__(self):
        """Iterate over property names."""
        return iter(self._properties.keys())

    def __getitem__(self, name: str) -> Any:
        """Get property value via dict-style access."""
        if name not in self._properties:
            raise KeyError(name)
        return self._values[name]

    def __setitem__(self, name: str, value: Any):
        """Set property value via dict-style access."""
        # KeyError propagates naturally from _set_property
        self._set_property(name, value)

    def __delitem__(self, name: str):
        """Delete property via dict-style access."""
        # KeyError propagates naturally from _del_property
        self._del_property(name)

    def __str__(self) -> str:
        """String representation."""
        props = ", ".join(
            f"{name}={self._values[name]!r}" for name in sorted(self._properties.keys())
        )
        return f"TyConf({props})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<TyConf with {len(self._properties)} properties>"

    def __hash__(self):
        """TyConf is unhashable (mutable object)."""
        raise TypeError("unhashable type: 'TyConf'")

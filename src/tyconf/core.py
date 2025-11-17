"""
TyConf - Core implementation for type-safe configuration management.

This module provides the core TyConf class and PropertyDescriptor for managing
configuration with runtime type validation.
"""

from typing import Any, Union, get_args, get_origin
from dataclasses import dataclass


@dataclass
class PropertyDescriptor:
    """Descriptor for a TyConf property."""

    name: str
    prop_type: type
    default_value: Any
    readonly: bool = False


class TyConf:
    """
    Type-safe configuration manager with runtime validation.

    TyConf (Typed Config) provides a robust way to manage application configuration
    with automatic type validation, read-only properties, and freeze/unfreeze capabilities.

    Examples:
        >>> config = TyConf(
        ...     host=(str, "localhost"),
        ...     port=(int, 8080),
        ...     debug=(bool, True)
        ... )
        >>> config.host
        'localhost'
        >>> config.port = 3000
        >>> config.port
        3000
    """

    # Constants for display formatting
    _MAX_DISPLAY_WIDTH = 80
    _PROPERTY_COL_WIDTH = 16
    _VALUE_COL_WIDTH = 14
    _TYPE_COL_WIDTH = 20
    _MAX_COLLECTION_ITEMS = 5
    _MAX_STRING_LENGTH = 50

    def __init__(self, **properties):
        """
        Initialize TyConf with properties.

        Args:
            **properties: Keyword arguments where each value is a tuple of
                         (type, default_value) or (type, default_value, readonly).

        Examples:
            >>> config = TyConf(
            ...     VERSION=(str, "1.0.0", True),
            ...     debug=(bool, False)
            ... )
        """
        # Internal storage
        object.__setattr__(self, "_properties", {})
        object.__setattr__(self, "_values", {})
        object.__setattr__(self, "_frozen", False)

        # Add properties
        for name, prop_def in properties.items():
            if len(prop_def) == 2:
                prop_type, default_value = prop_def
                readonly = False
            elif len(prop_def) == 3:
                prop_type, default_value, readonly = prop_def
            else:
                raise ValueError(
                    f"Property '{name}' must be (type, value) or (type, value, readonly)"
                )

            self.add(name, prop_type, default_value, readonly)

    def add(self, name: str, prop_type: type, default_value: Any, readonly: bool = False):
        """
        Add a new property to the TyConf.

        Args:
            name: Property name.
            prop_type: Expected type for the property.
            default_value: Default value for the property.
            readonly: If True, property cannot be modified after creation.

        Raises:
            AttributeError: If TyConf is frozen or property already exists.
            TypeError: If default_value doesn't match prop_type.

        Examples:
            >>> config = TyConf()
            >>> config.add('host', str, 'localhost')
            >>> config.host
            'localhost'
        """
        if self._frozen:
            raise AttributeError("Cannot add properties to frozen TyConf")

        if name in self._properties:
            raise AttributeError(f"Property '{name}' already exists")

        # Validate default value type
        self._validate_type(name, default_value, prop_type)

        # Store property descriptor and value
        self._properties[name] = PropertyDescriptor(
            name=name, prop_type=prop_type, default_value=default_value, readonly=readonly
        )
        self._values[name] = default_value

    def remove(self, name: str):
        """
        Remove a property from the TyConf.

        Args:
            name: Property name to remove.

        Raises:
            AttributeError: If TyConf is frozen or property doesn't exist.
            AttributeError: If property is read-only.

        Examples:
            >>> config = TyConf(debug=(bool, True))
            >>> config.remove('debug')
            >>> 'debug' in config
            False
        """
        if self._frozen:
            raise AttributeError("Cannot remove properties from frozen TyConf")

        if name not in self._properties:
            raise AttributeError(f"Property '{name}' does not exist")

        if self._properties[name].readonly:
            raise AttributeError(f"Cannot remove read-only property '{name}'")

        del self._properties[name]
        del self._values[name]

    def update(self, **kwargs):
        """
        Update multiple property values at once.

        Args:
            **kwargs: Property names and their new values.

        Raises:
            AttributeError: If any property is read-only or doesn't exist.
            TypeError: If any value doesn't match its property type.

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
        - Property types and readonly flags
        
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

    def get(self, name: str, default=None) -> Any:
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
        
        This method contains the shared logic for __setattr__ and __setitem__,
        following the DRY (Don't Repeat Yourself) principle.
        
        Args:
            name: Property name.
            value: Value to set.
            
        Raises:
            AttributeError: If TyConf is frozen or property is read-only.
            KeyError: If property doesn't exist (caller should catch and re-raise appropriately).
            TypeError: If value doesn't match property type.
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
        
        # Validate and set
        self._validate_type(name, value, prop.prop_type)
        self._values[name] = value

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
                getattr(arg, "__name__", str(arg))
                for arg in args
                if arg is not type(None)
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
                f"Property '{name}': expected {expected_name}, "
                f"got {type(value).__name__}"
            )

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
        if self._frozen:
            raise AttributeError("Cannot delete properties from frozen TyConf")

        if name not in self._properties:
            raise KeyError(name)

        if self._properties[name].readonly:
            raise AttributeError(f"Cannot delete read-only property '{name}'")

        del self._properties[name]
        del self._values[name]

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
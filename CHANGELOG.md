# Changelog

All notable changes to [TyConf](https://github.com/barabasz/tyconf) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Refactored `__setattr__()` and `__setitem__()` to use shared `_set_property()` helper method
- Improved code maintainability by eliminating duplication (DRY principle)
- Internal validation logic now centralized in single location for easier maintenance

## [1.0.0] - 2025-11-18

### Added
- Initial release of TyConf (Typed Config)
- Type-safe configuration management with runtime validation
- Support for basic Python types (str, int, float, bool, list, dict, tuple)
- Support for generic types (list[str], dict[str, int], etc.) from Python 3.9+
- Support for `Optional` and `Union` types from typing module
- Read-only properties to protect critical configuration values
- Freeze/unfreeze functionality for locking entire configuration
- Property management methods: `add()`, `remove()`, `update()`
- Configuration operations: `copy()`, `reset()`
- Dict-like interface with `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`
- Attribute-style access for intuitive property access
- Iteration support: `keys()`, `values()`, `items()`
- Property introspection: `get_property_info()`, `list_properties()`
- Display method `show()` for formatted output
- Comprehensive test suite with pytest (20 tests, 100% pass rate)
- Complete documentation (User Guide, API Reference, Best Practices)
- Example applications demonstrating real-world usage
- Zero external dependencies (pure Python)

### Fixed
- `_validate_type()` now correctly handles generic types (list[str], dict[str, int])
- Fixed `TypeError` when using `isinstance()` with parameterized generics
- Fixed Union types containing generics (e.g., `Union[list[int], str]`)
- `copy()` now preserves original default values for correct `reset()` behavior
- Copying modified configuration no longer breaks `reset()` functionality

### Changed
- Improved docstrings for `copy()` method with detailed examples
- Enhanced documentation with generic types examples
- Updated API reference with comprehensive type support section

## [0.9.5] - 2025-11-17

### Changed
- Package name: PyConf → TyConf
- All internal references and error messages updated to reflect new name
- Updated repository URLs and package metadata

## [0.9.4] - 2025-11-16

### Added
- Display formatting constants as class attributes
- Separate `_format_collection_item()` method for better formatting
- Support for `Optional` types from typing module
- Support for `Union` types from typing module

### Changed
- `is_frozen()` method replaced with `frozen` read-only property
- Improved None handling in Union types
- Refactored `_format_value_for_display()` for better maintainability

## [0.9.0] - 2025-11-15

### Added
- Read-only property support via third tuple parameter
- Freeze/unfreeze functionality for entire configuration
- `copy()` method for creating configuration copies
- `reset()` method for restoring default values

### Changed
- Improved type validation for Optional and Union types
- Enhanced error messages for type mismatches

## [0.8.0] - 2025-11-10

### Added
- `PropertyDescriptor` class for property metadata
- Runtime type validation with support for basic Python types
- Dict-like interface (`__getitem__`, `__setitem__`, `__contains__`, etc.)
- Attribute-style access for properties
- Special methods: `__len__`, `__iter__`, `__str__`, `__repr__`, `__hash__`

## [0.7.0] - 2025-11-08

### Added
- Initial core functionality
- Property management methods:
  - `add()` - Add new properties dynamically
  - `remove()` - Remove properties
  - `update()` - Update multiple properties at once
  - `copy()` - Create configuration copy
  - `reset()` - Reset to default values
  - `freeze()` / `unfreeze()` - Lock/unlock configuration
  - `show()` - Display all properties in formatted table
  - `get_property_info()` - Get property metadata
  - `list_properties()` - List all property names
  - `get()` - Get value with default fallback
- Iteration support (`keys()`, `values()`, `items()`)
- Basic type validation
- Internal storage with `_properties` and `_values` dictionaries

---

## Version History Summary

- **1.0.0** (2025-11-18) - Initial stable release with full feature set
- **0.9.5** (2025-11-17) - Renamed from PyConf to TyConf
- **0.9.4** (2025-11-16) - Added Optional/Union support
- **0.9.0** (2025-11-15) - Added read-only and freeze features
- **0.8.0** (2025-11-10) - Added dict-like interface
- **0.7.0** (2025-11-08) - Initial development version
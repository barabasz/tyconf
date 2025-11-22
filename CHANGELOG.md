# Changelog

All notable changes to [TyConf](https://github.com/barabasz/tyconf) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-01-22

### Fixed
- type declarations in core.py to comply with MyPy
- TypeError with Python 3.10+ union syntax (|) by handling types.UnionType
- OSError: File name too long when passing long strings to deserialization methods

## [1.2.0] - 2025-01-22

### Breaking Changes
- **Python 3.13+ Required** - minimum Python version increased from 3.10 to 3.13
  - Required for built-in `tomllib` support and improved type system features

### Added
- JSON & TOML Serialization - Export and import configurations to/from JSON/TOML format
- `from_env()` - Load configuration from environment variables with type conversion (class method)
- `load_env()` - Merge environment variables into existing configuration
- `to_dict()` - Export configuration to dictionary format
- `from_dict()` - Load configuration from dictionary (class method)
- Values-Only Export - Option to export only values without metadata

### Changed
- Environment variables are automatically converted to appropriate types
- Enhanced documentation with generic types examples
- Updated API reference with comprehensive type support section

### Notes
- Custom validator functions cannot be serialized to JSON/TOML
- Install with `pip install tyconf[toml]` to enable TOML export functionality
- When loading configurations with validators, provide validators separately using `add()` method

## [1.1.2] - 2025-11-22

### Added
- `try_set()` method to set a property value safely without raising exceptions
- new string validators: `min_length()`, `max_length()`, and `contains()`
- new numeric validators: `positive()`, `negative()`, `divisible_by()`, `is_even()`, `is_odd()`
- new path validators including `path_exists(),` `is_file()`, `is_directory()` and `file_extension()`

## [1.1.0] - 2025-11-18

### Breaking Changes
- **Python 3.10+ Required** - minimum Python version increased from 3.09 to 3.10

### Added
- Value Validation - Support for validators to check property values beyond type checking
- Auto-detection of third parameter: `bool` for readonly, `callable` for validator
- Validation on initialization, assignment, and update operations
- New tests for validator functionality (test_validators.py)

### Changed
- Property definition now supports: `(type, value)`, `(type, value, readonly)`, or `(type, value, validator)`
- Third parameter auto-detects type: if `bool` → readonly flag, if `callable` → validator
- Updated `PropertyDescriptor` to include optional `validator` field
- Enhanced `__init__()` to handle validator parameter
- Enhanced `add()` method with validator support
- Updated `_set_property()` to call validators on value changes
- Improved error messages for validation failures

### Fixed
- Validators and readonly are now mutually exclusive (as designed)
- Clear error message when third parameter is neither bool nor callable

## [1.0.2] - 2025-11-18

### Added
- Exception in `add()` for names starting with underscore
- Additional core tests to cover changed methods

### Changed
- Refactored `remove()` and `__delitem__()` to use shared `_del_property()` helper method
- Proper hint in get() method

## [1.0.1] - 2025-11-18

### Added
- Better error messages for invalid property definitions in constructor
- Validation that property definitions are tuples/lists (not single values)
- Helpful examples in error messages when property definition format is incorrect
- Type hints for class attributes (_properties, _values, _frozen) for better IDE support

### Changed
- Refactored `__setattr__()` and `__setitem__()` to use shared `_set_property()` helper method
- Improved code maintainability by eliminating duplication (DRY principle)
- Internal validation logic now centralized in single location for easier maintenance
- Enhanced `__init__()` to validate property definition format before processing
- Added PEP 526 compliant type annotations for instance attributes

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

- **1.2.0** (2025-11-20) - Added serialization/deserialization, required Python 3.13+
- **1.1.1** (2025-11-20) - Added try_set() method
- **1.1.0** (2025-11-18) - Added value validation with validators module, required Python 3.9+
- **1.0.2** (2025-11-18) - Code refactoring and improvements
- **1.0.1** (2025-11-18) - Better error messages
- **1.0.0** (2025-11-18) - Initial stable release with full feature set
- **0.9.5** (2025-11-17) - Renamed from PyConf to TyConf
- **0.9.4** (2025-11-16) - Added Optional/Union support
- **0.9.0** (2025-11-15) - Added read-only and freeze features
- **0.8.0** (2025-11-10) - Added dict-like interface
- **0.7.0** (2025-11-08) - Initial development version
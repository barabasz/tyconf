# Changelog

All notable changes to [TyConf](https://github.com/barabasz/tyconf) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-18

### Added
- Initial release of TyConf (Typed Config)
- Comprehensive test suite with pytest
- Complete documentation (User Guide, API Reference, Best Practices)
- Example applications demonstrating real-world usage

### Fixed
- `_validate_type()` now correctly handles generic types (list[str], dict[str, int])
- Fixed TypeError when using isinstance() with parameterized generics
- Fixed Union types containing generics (e.g., Union[list[int], str])
- `copy()` now preserves original default values for correct reset() behavior
- Copying modified configuration no longer breaks reset() functionality

### Changed
- Updated documentation and examples
- Improved docstrings for `copy()` method

### 0.9.5 (2025-11-17)

### Changed
- Package name: PyConf → TyConf
- All internal references and error messages updated

### 0.9.4 (2025-11-16)

### Added
- Display formatting constants as class attributes
- Separate `_format_collection_item()` method
- Support for `Optional` types from typing module
- Support for `Union` types from typing module

### Changed
- `is_frozen()` method to `frozen` read-only property
- Improved None handling in Union types
- Refactored `_format_value_for_display()`

### 0.9.0 (2025-11-15)

### Added
- Read-only property support
- Added freeze/unfreeze functionality
- Added copy() and reset() methods
- Added read-only properties support

### Changed
- Improved type validation for Optional and Union types

### 0.8.0 (2025-11-10)

### Added
- `PropertyDescriptor` class for property metadata
- Runtime type validation with support for basic Python types
- Dict-like interface (`__getitem__`, `__setitem__`, `__contains__`, etc.)
- Attribute-style access for properties

### 0.7.0 (2025-11-08)

### Added
- Property management methods:
  - `add()` - Add new properties
  - `remove()` - Remove properties
  - `update()` - Update multiple properties
  - `copy()` - Create configuration copy
  - `reset()` - Reset to default values
  - `freeze()` / `unfreeze()` - Lock/unlock configuration
  - `show()` - Display all properties in formatted table
  - `get_property_info()` - Get property metadata
  - `list_properties()` - List all property names
  - `get()` - Get value with default fallback
- Iteration support (`keys()`, `values()`, `items()`)
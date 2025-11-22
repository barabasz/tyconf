# TyConf User Guide

Complete guide to using TyConf for type-safe configuration management.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Type Validation](#type-validation)
5. [Read-Only Properties](#read-only-properties)
6. [Freeze and Unfreeze](#freeze-and-unfreeze)
7. [Property Management](#property-management)
8. [Dict-Like Interface](#dict-like-interface)
9. [Iteration](#iteration)
10. [Serialization and Deserialization](#serialization-and-deserialization)
11. [Advanced Features](#advanced-features)
12. [Common Mistakes](#common-mistakes)

---

## Introduction

**TyConf** (Typed Config) is a modern Python library for managing application configuration with runtime type validation. It provides an intuitive API with both attribute and dict-style access, making it easy to work with configuration in any Python application. TyConf requiress Python 3.13+.

### Why TyConf?

- ✅ **Type Safety**: Automatic validation prevents type-related bugs
- ✅ **Flexibility**: Support for Optional and Union types
- ✅ **Protection**: Read-only properties and freeze/unfreeze
- ✅ **Simplicity**: Intuitive API that feels natural in Python
- ✅ **Zero Dependencies**: Pure Python with no external requirements

---

## Installation

```bash
pip install tyconf
```

**Requirements:** Python 3.13+

**Optional Dependencies:**
```bash
# For TOML export support (TOML import is built-in via tomllib)
pip install tyconf[toml]
```

---

## Basic Usage

### Creating Configuration

Create a TyConf instance with initial properties:

```python
from tyconf import TyConf

config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)
```

Each property is defined as a tuple: `(type, default_value)`

**Important:** Always use tuples, not single values!

```python
# ❌ Wrong - will raise TypeError
config = TyConf(debug=True)

# ✅ Correct
config = TyConf(debug=(bool, True))
```

### Accessing Values

Access values using attribute or dict-style syntax:

```python
# Attribute style
print(config.host)      # 'localhost'
print(config.port)      # 8080

# Dict style
print(config['host'])   # 'localhost'
print(config['port'])   # 8080
```

### Modifying Values

Modify values the same way:

```python
# Attribute style
config.debug = False
config.port = 3000

# Dict style
config['debug'] = True
config['port'] = 8080
```

All modifications are type-checked automatically!

---

## Type Validation

TyConf validates types at runtime, preventing bugs:

```python
config = TyConf(
    name=(str, "MyApp"),
    port=(int, 8080),
    timeout=(float, 30.0)
)

# Valid assignments
config.name = "NewApp"      # ✓ str
config.port = 3000          # ✓ int
config.timeout = 60.5       # ✓ float

# Invalid assignments
config.port = "8080"        # ✗ TypeError: expected int, got str
config.timeout = "30"       # ✗ TypeError: expected float, got str
```

### Optional Types

Use `Optional` for properties that can be `None`:

```python
from typing import Optional

config = TyConf(
    api_key=(Optional[str], None),
    timeout=(Optional[int], 30)
)

# All valid
config.api_key = "secret123"
config.api_key = None
config.timeout = None
config.timeout = 60
```

### Union Types

Use `Union` for properties that accept multiple types:

```python
from typing import Union

config = TyConf(
    port=(Union[int, str], 8080),
    workers=(Union[int, str], 4)
)

# All valid
config.port = 3000          # int
config.port = "auto"        # str
config.workers = 8          # int
config.workers = "max"      # str

# Invalid
config.port = 3.14          # TypeError: float not in Union[int, str]
```

### Generic Types (Python 3.9+)

TyConf supports generic type annotations:

```python
config = TyConf(
    tags=(list[str], []),
    mapping=(dict[str, int], {}),
    coordinates=(tuple[float, float], (0.0, 0.0))
)

# Valid assignments
config.tags = ["python", "config", "typed"]
config.mapping = {"count": 42, "total": 100}
config.coordinates = (51.5074, -0.1278)

# Type validation still works
config.tags = "not a list"  # TypeError: expected list, got str
```

---

## Read-Only Properties

Protect critical configuration from modification with read-only properties:

```python
config = TyConf(
    VERSION=(str, "1.0.0", True),     # Read-only
    ENVIRONMENT=(str, "prod", True),   # Read-only
    debug=(bool, False)                # Mutable
)

# Read values normally
print(config.VERSION)       # '1.0.0'
print(config.ENVIRONMENT)   # 'prod'

# Modify mutable properties
config.debug = True         # ✓ OK

# Cannot modify read-only properties
config.VERSION = "2.0.0"    # ✗ AttributeError: read-only
```

Read-only properties are perfect for:
- Application version numbers
- Environment names (dev, staging, prod)
- System constants
- Maximum upload sizes
- API endpoints

---

## Freeze and Unfreeze

Lock the entire configuration to prevent any modifications:

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)

# Normal operation
config.port = 3000          # ✓ OK

# Freeze configuration
config.freeze()
print(config.frozen)        # True

# Cannot modify when frozen
config.port = 8080          # ✗ AttributeError: frozen
config.debug = False        # ✗ AttributeError: frozen

# Unfreeze to allow modifications
config.unfreeze()
print(config.frozen)        # False
config.port = 8080          # ✓ OK now
```

**Use Cases for Freezing:**

1. **Production Safety**: Freeze configuration after loading to prevent accidental changes during runtime
2. **Testing**: Freeze test fixtures to ensure consistent test environments
3. **Multi-threading**: Freeze shared configuration before spawning threads
4. **Deployment**: Lock configuration after validation before starting services

---

## Property Management

### Adding Properties

Add properties dynamically after creation:

```python
config = TyConf()

config.add('host', str, 'localhost')
config.add('port', int, 8080)
config.add('VERSION', str, '1.0.0', readonly=True)

print(config.host)  # 'localhost'
```

### Removing Properties

Remove properties (except read-only ones):

```python
config = TyConf(
    temp=(str, "value"),
    debug=(bool, True)
)

config.remove('temp')
print('temp' in config)  # False

# Cannot remove read-only properties
# config.remove('VERSION')  # Raises AttributeError
```

### Updating Multiple Properties

Update several properties at once:

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, False)
)

config.update(
    host="0.0.0.0",
    port=3000,
    debug=True
)
```

### Copying Configuration

Create an independent copy that preserves original default values:

```python
original = TyConf(
    debug=(bool, True),
    port=(int, 8080)
)

# Modify values
original.debug = False
original.port = 3000

# Create copy - preserves current values
copy = original.copy()
print(copy.debug)      # False (current value)
print(copy.port)       # 3000 (current value)

# Reset restores ORIGINAL defaults
copy.reset()
print(copy.debug)      # True (original default)
print(copy.port)       # 8080 (original default)
```

**Important:** The copy preserves original default values, ensuring that `reset()` works correctly even on modified configurations.

### Resetting to Defaults

Reset all mutable properties to their default values:

```python
config = TyConf(
    VERSION=(str, "1.0", True),  # Read-only
    debug=(bool, False),         # Mutable
    port=(int, 8080)             # Mutable
)

# Modify values
config.debug = True
config.port = 3000

# Reset to defaults
config.reset()

print(config.debug)     # False (reset)
print(config.port)      # 8080 (reset)
print(config.VERSION)   # '1.0' (unchanged - read-only)
```

### Reserved Names

Property names starting with an underscore (`_`) are reserved for internal use and cannot be used. Attempting to define a property like `_private` will raise a `ValueError`.

```python
# ❌ Wrong - underscore prefix is reserved
# config = TyConf(_private=(str, "value"))  # Raises ValueError

# ✅ Correct - use regular names
config = TyConf(private=(str, "value"))
```

---

## Dict-Like Interface

TyConf supports standard dict operations:

### Check if Property Exists

```python
config = TyConf(host=(str, "localhost"))

if 'host' in config:
    print("Host configured")

if 'missing' not in config:
    print("Property doesn't exist")
```

### Get with Default

```python
host = config.get('host', 'localhost')
missing = config.get('missing', 'default')
```

### Delete Properties

```python
config = TyConf(temp=(str, "value"))

del config['temp']
print('temp' in config)  # False
```

### Length

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)

print(len(config))  # 3
```

---

## Iteration

Iterate over properties in multiple ways:

### Iterate Over Names

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)

# Using the iterator
for name in config:
    print(name)

# Using keys()
for name in config.keys():
    print(name)
```

### Iterate Over Values

```python
for value in config.values():
    print(value)
```

### Iterate Over Items

```python
for name, value in config.items():
    print(f"{name} = {value}")
```

### List All Properties

```python
properties = config.list_properties()
print(properties)  # ['host', 'port', 'debug']
```

---

## Serialization and Deserialization

TyConf provides comprehensive support for exporting and importing configurations in multiple formats: JSON, TOML, and environment variables.

### JSON Serialization

#### Export to JSON

Export configurations to JSON format with full metadata or values only:

```python
from tyconf import TyConf

config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)

# Export with full metadata (includes types, defaults, readonly flags)
config.to_json('config.json')

# Export values only (simpler format)
config.to_json('values.json', values_only=True)
```

**Full metadata format:**
```json
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
    },
    "debug": {
      "type": "bool",
      "value": true,
      "default": true,
      "readonly": false
    }
  }
}
```

**Values-only format:**
```json
{
  "host": "localhost",
  "port": 8080,
  "debug": true
}
```

#### Import from JSON

Load configurations from JSON files:

```python
# Load from full metadata format
config = TyConf.from_json('config.json')

# Access properties
print(config.host)  # 'localhost'
print(config.port)  # 8080
```

#### Merge JSON into Existing Config

Update an existing configuration with values from JSON:

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, False)
)

# Merge values from JSON file (only updates existing properties)
config.load_json('overrides.json')
```

### TOML Serialization

#### Export to TOML

Export configurations to TOML format:

```python
# Export to TOML (requires: pip install tyconf[toml])
config.to_toml('config.toml')

# Export values only
config.to_toml('values.toml', values_only=True)
```

**Note:** TOML export requires the `tomli-w` package. Install with:
```bash
pip install tyconf[toml]
```

**Full metadata format:**
```toml
_tyconf_version = "1.2.0"

[properties.host]
type = "str"
value = "localhost"
default = "localhost"
readonly = false

[properties.port]
type = "int"
value = 8080
default = 8080
readonly = false
```

**Values-only format:**
```toml
host = "localhost"
port = 8080
debug = true
```

#### Import from TOML

Load configurations from TOML files (built-in via `tomllib`):

```python
# Load from TOML (no extra dependency needed for import)
config = TyConf.from_toml('config.toml')

print(config.host)  # 'localhost'
```

### Environment Variables

#### Load from Environment Variables

Create configurations from environment variables with automatic type conversion:

```python
import os

# Set environment variables
os.environ['APP_HOST'] = 'production.example.com'
os.environ['APP_PORT'] = '3000'
os.environ['APP_DEBUG'] = 'false'

# Load from environment with schema
config = TyConf.from_env(
    prefix='APP_',
    schema={
        'host': str,
        'port': int,
        'debug': bool
    }
)

print(config.host)   # 'production.example.com'
print(config.port)   # 3000 (converted to int)
print(config.debug)  # False (converted to bool)
```

**Type Conversion Rules:**

- **Boolean**: `"true"`, `"yes"`, `"1"` → `True`; `"false"`, `"no"`, `"0"` → `False` (case-insensitive)
- **Integer**: Converted using `int()`
- **Float**: Converted using `float()`
- **String**: Used as-is
- **List**: JSON format, e.g., `'["item1", "item2"]'`
- **Dict**: JSON format, e.g., `'{"key": "value"}'`

#### Merge Environment Variables

Update existing configuration with environment variables:

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, False)
)

# Override with environment variables
config.load_env(prefix='APP_')
```

### Dictionary Export/Import

Low-level dictionary serialization:

```python
# Export to dictionary
data = config.to_dict()
print(data)
# {
#   "_tyconf_version": "1.2.0",
#   "properties": {...}
# }

# Export values only
values = config.to_dict(values_only=True)
print(values)
# {"host": "localhost", "port": 8080, "debug": true}

# Load from dictionary
config = TyConf.from_dict(data)
```

### Values-Only vs Full Metadata

Choose the appropriate export format based on your use case:

#### Full Metadata Format

**Advantages:**
- Preserves complete configuration structure
- Includes type information for validation
- Stores default values for reset functionality
- Maintains readonly flags
- Can fully reconstruct TyConf objects

**Use when:**
- Saving complete application state
- Need to restore configuration exactly
- Want type validation on reload
- Need to preserve readonly properties

#### Values-Only Format

**Advantages:**
- Simpler, more readable format
- Compatible with other tools
- Smaller file size
- Easy to edit manually
- Standard JSON/TOML format

**Use when:**
- Sharing configs with non-TyConf applications
- Manual editing is required
- File size matters
- Integration with external systems
- Simple override files

### Validator Limitations

**Important:** Custom validator functions cannot be serialized to JSON/TOML.

```python
from tyconf.validators import range

config = TyConf(
    port=(int, 8080, range(1024, 65535))
)

# Export works, but validator is not saved
config.to_json('config.json')

# When loading, provide validators separately
loaded = TyConf.from_json('config.json')
# Validator is lost - need to re-add it
loaded.remove('port')
loaded.add('port', int, 8080, validator=range(1024, 65535))
```

**Workaround:** Use values-only export and define validators in code:

```python
# Export values only
config.to_json('values.json', values_only=True)

# Define validators in application code
def create_config():
    config = TyConf.from_json('values.json')
    
    # Re-add validators if needed
    port_value = config.port
    config.remove('port')
    config.add('port', int, port_value, validator=range(1024, 65535))
    
    return config
```

---

## Advanced Features

### Display Configuration

Pretty-print all properties:

```python
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)

config.show()
```

Output:
```
Configuration properties:
--------------------------------------------
debug            = True            bool
host             = 'localhost'     str
port             = 8080            int
--------------------------------------------
```

### Get Property Metadata

Access property information:

```python
config = TyConf(VERSION=(str, "1.0.0", True))

info = config.get_property_info('VERSION')
print(info.name)           # 'VERSION'
print(info.prop_type)      # <class 'str'>
print(info.default_value)  # '1.0.0'
print(info.readonly)       # True
```

### String Representation

```python
config = TyConf(host=(str, "localhost"), port=(int, 8080))

print(str(config))   # TyConf(host='localhost', port=8080)
print(repr(config))  # <TyConf with 2 properties>
```

---

## Common Mistakes

### Mistake 1: Using Single Values Instead of Tuples

**❌ Wrong:**
```python
# config = TyConf(debug=True)
# TypeError: Property 'debug': expected tuple (type, value) or (type, value, readonly), 
# got bool. Example: debug=(bool, True)
```

**✅ Correct:**
```python
config = TyConf(debug=(bool, True))
```

### Mistake 2: Wrong Number of Tuple Elements

**❌ Wrong:**
```python
# config = TyConf(port=(int,))
# ValueError: Property 'port': expected tuple of 2 or 3 elements, got 1.
# Valid formats: (port=(type, value)) or (port=(type, value, readonly))
```

**✅ Correct:**
```python
config = TyConf(port=(int, 8080))
# or
config = TyConf(port=(int, 8080, False))
```

### Mistake 3: Too Many Tuple Elements

**❌ Wrong:**
```python
# config = TyConf(debug=(bool, True, False, "extra"))
# ValueError: Property 'debug': expected tuple of 2 or 3 elements, got 4.
```

**✅ Correct:**
```python
config = TyConf(debug=(bool, True))
# or with readonly flag
config = TyConf(debug=(bool, True, False))
```

### Mistake 4: Providing String Instead of Tuple

**❌ Wrong:**
```python
# config = TyConf(host="localhost")
# TypeError: Property 'host': expected tuple (type, value) or (type, value, readonly),
# got str. Example: host=(str, 'localhost')
```

**✅ Correct:**
```python
config = TyConf(host=(str, "localhost"))
```

### Mistake 5: Forgetting Type Annotation

**❌ Wrong (but works):**
```python
# This works but you lose type checking benefits
config = TyConf(data=(list, ["a", "b"]))
config.data = [1, 2, 3]  # No validation - allows mixed types
```

**✅ Better:**
```python
# Use specific type annotations
config = TyConf(data=(list[str], ["a", "b"]))
config.data = ["x", "y", "z"]  # Validated as list
```

### Mistake 6: Modifying Frozen Configuration

**❌ Wrong:**
```python
config = TyConf(port=(int, 8080))
config.freeze()
# config.port = 3000
# AttributeError: Cannot modify frozen TyConf
```

**✅ Correct:**
```python
config = TyConf(port=(int, 8080))
config.freeze()
config.unfreeze()  # Unfreeze first
config.port = 3000  # Now OK
```

### Mistake 7: Modifying Read-Only Properties

**❌ Wrong:**
```python
config = TyConf(VERSION=(str, "1.0.0", True))
# config.VERSION = "2.0.0"
# AttributeError: Property 'VERSION' is read-only
```

**✅ Correct:**
```python
# Read-only properties cannot be modified
# If you need to change it, don't make it read-only
config = TyConf(VERSION=(str, "1.0.0"))  # Not read-only
config.VERSION = "2.0.0"  # OK
```

### Summary of Property Definition Formats

| Format | Elements | Example | Use Case |
|--------|----------|---------|----------|
| `(type, value)` | 2 | `debug=(bool, True)` | Mutable property |
| `(type, value, False)` | 3 | `debug=(bool, True, False)` | Explicitly mutable |
| `(type, value, True)` | 3 | `VERSION=(str, "1.0", True)` | Read-only property |

**Remember:** Always use tuples with 2 or 3 elements!

---

## Real-World Example

Here's a complete example for a web application:

```python
from tyconf import TyConf
from typing import Optional
import os

# Define configuration with proper tuple format
app_config = TyConf(
    # Metadata (read-only)
    APP_NAME=(str, "WebAPI", True),
    VERSION=(str, "2.0.0", True),
    ENVIRONMENT=(str, os.getenv('ENV', 'development'), True),
    
    # Server settings (mutable)
    host=(str, "localhost"),
    port=(int, 5000),
    debug=(bool, True),
    workers=(int, 4),
    
    # Database (mutable)
    database_url=(Optional[str], None),
    db_pool_size=(int, 10),
    
    # Features (mutable)
    enable_api=(bool, True),
    rate_limit=(Optional[int], 100)
)

# Configure from environment
app_config.debug = os.getenv('DEBUG', 'false').lower() == 'true'
app_config.port = int(os.getenv('PORT', '5000'))
app_config.database_url = os.getenv('DATABASE_URL')

# Display configuration
print(f"Starting {app_config.APP_NAME} v{app_config.VERSION}")
app_config.show()

# Freeze before starting app
app_config.freeze()
print("Configuration locked!")

# Start your application...
```

This pattern ensures:
1. Type safety for all configuration
2. Environment-specific overrides
3. Protection from runtime modifications
4. Clear visibility into current settings

---

## Next Steps

- Check out the [API Reference](api_reference.md) for complete method documentation
- See [Best Practices](best_practices.md) for tips on effective usage
- Explore the [examples/](../examples/) directory for more code samples
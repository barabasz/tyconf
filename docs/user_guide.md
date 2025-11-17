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
10. [Advanced Features](#advanced-features)

---

## Introduction

**TyConf** (Typed Config) is a Python library for managing application configuration with runtime type validation. It provides an intuitive API with both attribute and dict-style access, making it easy to work with configuration in any Python application.

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
config.remove('VERSION')  # AttributeError
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

Create an independent copy:

```python
original = TyConf(
    debug=(bool, True),
    port=(int, 8080)
)
original.freeze()

# Create unfrozen copy
copy = original.copy()
print(copy.frozen)      # False
copy.debug = False      # Doesn't affect original
```

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
print(properties)  # ['debug', 'host', 'port']
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

## Real-World Example

Here's a complete example for a web application:

```python
from tyconf import TyConf
from typing import Optional
import os

# Define configuration
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
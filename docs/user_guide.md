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
11. [Common Mistakes](#common-mistakes)

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

## Value Validation

Beyond type validation, TyConf supports value validation through validators. Validators ensure that values meet specific criteria such as ranges, patterns, or custom business rules.

### Using Lambda Validators

For simple validation logic, use lambda functions:

```python
config = TyConf(
    # Port must be greater than 1024
    port=(int, 8080, lambda x: x > 1024),
    
    # Username must be non-empty
    username=(str, "admin", lambda x: len(x) > 0),
    
    # Count must be even
    even_count=(int, 10, lambda x: x % 2 == 0)
)

# Valid assignments
config.port = 3000        # OK
config.username = "john"  # OK
config.even_count = 4     # OK

# Invalid assignments
# config.port = 80         # ValueError: Validation failed
# config.username = ""     # ValueError: Validation failed
# config.even_count = 3    # ValueError: Validation failed
```

Lambda validators should return:
- `True` if the value is valid
- `False` if the value is invalid (raises generic error)
- `None` to skip validation

### Using Custom Validator Functions

For complex validation with meaningful error messages, create validator functions:

```python
def validate_email(value):
    """Validate email format."""
    if '@' not in value or '.' not in value:
        raise ValueError(f"Invalid email address: {value}")
    return True

def validate_password(value):
    """Validate password strength."""
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain an uppercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain a number")
    return True

config = TyConf(
    email=(str, "user@example.com", validate_email),
    password=(str, "Secret123", validate_password)
)

# Valid
config.email = "test@domain.com"  # OK

# Invalid with custom error messages
# config.email = "invalid-email"
# ValueError: Invalid email address: invalid-email

# config.password = "weak"
# ValueError: Password must be at least 8 characters
```

### Built-in Validators

TyConf provides several built-in validators in the `tyconf.validators` module:

#### Numeric Range Validation

```python
from tyconf.validators import range

config = TyConf(
    port=(int, 8080, range(1024, 65535)),
    temperature=(float, 20.0, range(-50.0, 50.0)),
    percentage=(int, 50, range(0, 100))
)

config.port = 3000         # OK
# config.port = 80         # ValueError: Value 80 not in range [1024, 65535]
```

#### Length Validation

```python
from tyconf.validators import length

config = TyConf(
    username=(str, "admin", length(3, 20)),
    password=(str, "secret123", length(8)),  # Minimum only
    tags=(list, [], length(1, 5))
)

config.username = "john"      # OK
# config.username = "ab"      # ValueError: Length 2 not in range [3, 20]
config.tags = ["python"]      # OK
# config.tags = []            # ValueError: Length 0 not in range [1, 5]
```

#### Pattern Matching

```python
from tyconf.validators import regex

config = TyConf(
    email=(str, "user@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    phone=(str, "555-1234", regex(r'^\d{3}-\d{4}$')),
    code=(str, "ABC123", regex(r'^[A-Z]{3}\d{3}$'))
)

config.email = "test@domain.com"  # OK
# config.email = "invalid"        # ValueError: Value does not match pattern
```

#### Allowed Values

```python
from tyconf.validators import one_of

config = TyConf(
    environment=(str, "development", one_of("development", "staging", "production")),
    log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR"))
)

config.environment = "production"  # OK
# config.environment = "test"      # ValueError: Value 'test' not in allowed values
```

#### Combining Validators

Use `all_of()` when all validators must pass:

```python
from tyconf.validators import all_of, length, regex

config = TyConf(
    # Username must be 3-20 chars AND alphanumeric
    username=(str, "admin", all_of(
        length(3, 20),
        regex(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    ))
)

config.username = "john_doe"    # OK
# config.username = "ab"        # ValueError: Failed length validator
# config.username = "123user"   # ValueError: Failed regex validator
```

Use `any_of()` when at least one validator must pass:

```python
from tyconf.validators import any_of, range, one_of

config = TyConf(
    # Port can be in range OR special value (0 = auto)
    port=(int, 8080, any_of(
        range(1024, 65535),
        one_of(0)
    ))
)

config.port = 3000   # OK (in range)
config.port = 0      # OK (special value)
# config.port = 80   # ValueError: None of the validators passed
```

#### Disallowed Values

```python
from tyconf.validators import not_in

config = TyConf(
    username=(str, "john", not_in("root", "admin", "administrator")),
    port=(int, 8080, not_in(22, 23, 25))  # Reserved ports
)

config.username = "mary"  # OK
# config.username = "root"  # ValueError: Value 'root' is not allowed
```

### Validation Timing

Validators are executed at three key points:

1. **Initialization**: When creating the property
```python
# Validates the initial value (8080)
config = TyConf(port=(int, 8080, range(1024, 65535)))
```

2. **Assignment**: When changing the value
```python
config.port = 3000  # Validates 3000
```

3. **Update**: When using the update() method
```python
config.update(port=9000)  # Validates 9000
```

### Validators vs Read-Only

**Important:** Validators and readonly are mutually exclusive - you cannot use both on the same property.

```python
# ❌ Wrong - cannot have both
# This is not valid because the third parameter is auto-detected:
# - If it's a bool → readonly
# - If it's a callable → validator

# ✅ Correct - use one or the other
config = TyConf(
    VERSION=(str, "1.0.0", True),              # Read-only (bool)
    port=(int, 8080, range(1024, 65535)),      # Validator (callable)
    debug=(bool, False)                        # Neither (mutable)
)
```

The third parameter is auto-detected:
- If `bool`: Sets the readonly flag
- If `callable`: Sets a validator function

### Complete Validation Example

Here's a comprehensive example using multiple validation types:

```python
from tyconf import TyConf
from tyconf.validators import range, length, regex, one_of, all_of
from typing import Optional

def validate_url(value):
    """Custom URL validator."""
    if value and not value.startswith(('http://', 'https://')):
        raise ValueError(f"URL must start with http:// or https://: {value}")
    return True

# Application configuration with validation
config = TyConf(
    # Metadata (read-only, no validation needed)
    APP_NAME=(str, "MyWebApp", True),
    VERSION=(str, "1.0.0", True),
    
    # Server settings with validation
    host=(str, "localhost"),
    port=(int, 8080, range(1024, 65535)),
    workers=(int, 4, range(1, 16)),
    
    # Database with validation
    database_url=(Optional[str], None, validate_url),
    db_pool_size=(int, 10, range(5, 100)),
    
    # User settings with complex validation
    admin_email=(str, "admin@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    environment=(str, "development", one_of("development", "staging", "production")),
    
    # Password with multiple validators
    api_key=(str, "Secret123!", all_of(
        length(8, 64),
        regex(r'.*[A-Z].*'),  # Must have uppercase
        regex(r'.*[0-9].*')   # Must have digit
    ))
)

# All assignments are validated
config.port = 3000                      # OK
# config.port = 80                      # ValueError: out of range
config.environment = "production"       # OK
# config.environment = "test"           # ValueError: not in allowed values
config.database_url = "https://db.com"  # OK
# config.database_url = "ftp://db.com"  # ValueError: invalid URL
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
# or with validator
config = TyConf(debug=(bool, True, lambda x: isinstance(x, bool)))
```

**Note:** The third parameter is auto-detected - if it's a `bool`, it sets readonly; if it's a `callable`, it sets a validator.

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
| `(type, value, callable)` | 3 | `port=(int, 8080, lambda x: x > 1024)` | Property with validator |

**Remember:** 
- Always use tuples with 2 or 3 elements!
- The third parameter is auto-detected: `bool` → readonly, `callable` → validator
- Validators and readonly are mutually exclusive

---

## Real-World Example

Here's a complete example for a web application:

```python
from tyconf import TyConf
from tyconf.validators import range, regex, one_of
from typing import Optional
import os

def validate_db_url(value):
    """Validate database URL format."""
    if value and not any(value.startswith(p) for p in ['postgresql://', 'mysql://', 'sqlite://']):
        raise ValueError("Database URL must start with postgresql://, mysql://, or sqlite://")
    return True

# Define configuration with proper tuple format
app_config = TyConf(
    # Metadata (read-only)
    APP_NAME=(str, "WebAPI", True),
    VERSION=(str, "2.0.0", True),
    ENVIRONMENT=(str, os.getenv('ENV', 'development'), True),
    
    # Server settings (mutable with validation)
    host=(str, "localhost"),
    port=(int, 5000, range(1024, 65535)),
    debug=(bool, True),
    workers=(int, 4, range(1, 16)),
    
    # Database (mutable with validation)
    database_url=(Optional[str], None, validate_db_url),
    db_pool_size=(int, 10, range(5, 100)),
    
    # Features (mutable with validation)
    enable_api=(bool, True),
    rate_limit=(Optional[int], 100, range(1, 10000)),
    log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    admin_email=(Optional[str], None, regex(r'^[\w\.-]+@[\w\.-]+\.\w+$'))
)

# Configure from environment (with validation)
app_config.debug = os.getenv('DEBUG', 'false').lower() == 'true'
app_config.port = int(os.getenv('PORT', '5000'))
app_config.database_url = os.getenv('DATABASE_URL')
if os.getenv('LOG_LEVEL'):
    app_config.log_level = os.getenv('LOG_LEVEL')

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
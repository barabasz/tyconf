# TyConf API Reference

Complete API documentation for TyConf.

## Classes

### TyConf

Main configuration manager class with type-safe properties.

#### Constructor

```python
TyConf(**properties)
```

**Parameters:**
- `**properties`: Keyword arguments where each value is a tuple:
  - `(type, default_value)` - Regular property
  - `(type, default_value, third_param)` - Property with auto-detected third parameter:
    - If `third_param` is `bool`: Sets readonly flag (backward compatible)
    - If `third_param` is `callable`: Sets validator function

**Raises:**
- `TypeError`: If a property definition is not a tuple or list, or if third parameter is neither bool nor callable.
- `ValueError`: If a property definition tuple has the wrong number of elements, if a property name starts with an underscore (`_`), or if validator fails.

**Example:**
```python
from tyconf import TyConf
from tyconf.validators import range

config = TyConf(
    VERSION=(str, "1.0.0", True),           # Read-only (bool = readonly)
    port=(int, 8080, range(1024, 65535)),  # Validator (callable = validator)
    debug=(bool, False)                     # Mutable
)

# This will raise ValueError because the name starts with an underscore
# config = TyConf(_internal=(int, 123))
```

**Note:** The third parameter is auto-detected: if it's a `bool`, it sets the readonly flag; if it's a `callable`, it sets a validator. Validators and readonly are mutually exclusive - you cannot have both on the same property.

#### Methods

##### add()

```python
add(name: str, prop_type: type, default_value: Any, readonly: bool = False, validator: callable = None)
```

Add a new property to the configuration.

**Parameters:**
- `name`: Property name
- `prop_type`: Expected type (supports `Optional`, `Union`, and generics like `list[str]`)
- `default_value`: Default value for the property
- `readonly`: If `True`, property cannot be modified after creation (mutually exclusive with validator)
- `validator`: Optional callable to validate values (mutually exclusive with readonly)

**Raises:**
- `AttributeError`: If TyConf is frozen or property already exists
- `ValueError`: If the property name is reserved (starts with an underscore `_`), or if both readonly and validator are specified
- `TypeError`: If default_value doesn't match prop_type

**Example:**
```python
from tyconf.validators import range, regex

config = TyConf()
config.add('host', str, 'localhost')
config.add('tags', list[str], [])
config.add('VERSION', str, '1.0.0', readonly=True)
config.add('port', int, 8080, validator=range(1024, 65535))
config.add('email', str, 'user@example.com', validator=regex(r'^[\w\.-]+@[\w\.-]+\.\w+$'))

# This will raise ValueError
# config.add('_secret', str, 'value')

# This will raise ValueError (cannot have both readonly and validator)
# config.add('test', str, 'value', readonly=True, validator=lambda x: len(x) > 0)
```

##### remove()

```python
remove(name: str)
```

Remove a property from the configuration.

**Parameters:**
- `name`: Property name to remove

**Raises:**
- `AttributeError`: If TyConf is frozen, property doesn't exist, or property is read-only
- `KeyError`: If property doesn't exist

**Example:**
```python
config.remove('debug')
```

##### update()

```python
update(**kwargs)
```

Update multiple property values at once.

**Parameters:**
- `**kwargs`: Property names and their new values

**Raises:**
- `AttributeError`: If any property is read-only or doesn't exist
- `TypeError`: If any value doesn't match its property type
- `ValueError`: If any value fails validator

**Example:**
```python
config.update(host="0.0.0.0", port=3000, debug=True)
```

##### copy()

```python
copy() -> TyConf
```

Create an unfrozen copy of the configuration.

The copy preserves:
- **Original default values** (so `reset()` restores to original defaults, not copied values)
- **Current property values**
- **Property types, readonly flags, and validators**

The copy is always unfrozen, even if the original is frozen.

**Returns:**
- New `TyConf` instance with same properties and current values

**Example:**
```python
config = TyConf(
    debug=(bool, True), 
    port=(int, 8080, range(1024, 65535))
)

# Modify values
config.debug = False
config.port = 3000
config.freeze()

# Create copy - preserves current values and validators
backup = config.copy()
backup.frozen        # False (copy is unfrozen)
backup.debug         # False (current value)
backup.port          # 3000 (current value)

# Validator is preserved
backup.port = 80     # ValueError: must be >= 1024

# Reset restores ORIGINAL defaults, not copied values
backup.reset()
backup.debug         # True (original default)
backup.port          # 8080 (original default)
```

**Important:** The copy preserves original default values and validators, ensuring that `reset()` and validation work correctly even on modified configurations.

##### reset()

```python
reset()
```

Reset all mutable properties to their default values. Read-only properties are not affected.

**Raises:**
- `AttributeError`: If TyConf is frozen

**Example:**
```python
config = TyConf(debug=(bool, False))
config.debug = True
config.reset()
# config.debug is now False
```

##### freeze()

```python
freeze()
```

Freeze the configuration, preventing all modifications.

**Example:**
```python
config.freeze()
# config.debug = False  # Raises AttributeError
```

##### unfreeze()

```python
unfreeze()
```

Unfreeze the configuration, allowing modifications.

**Example:**
```python
config.unfreeze()
config.debug = False  # OK now
```

##### show()

```python
show()
```

Display all properties in a formatted table.

**Example:**
```python
config.show()
# Output:
# Configuration properties:
# --------------------------------------------
# debug            = False           bool
# host             = 'localhost'     str
# port             = 8080            int
# --------------------------------------------
```

##### get_property_info()

```python
get_property_info(name: str) -> PropertyDescriptor
```

Get metadata for a property.

**Parameters:**
- `name`: Property name

**Returns:**
- `PropertyDescriptor` with property metadata

**Raises:**
- `AttributeError`: If property doesn't exist

**Example:**
```python
info = config.get_property_info('VERSION')
print(info.name)           # 'VERSION'
print(info.prop_type)      # <class 'str'>
print(info.default_value)  # '1.0.0'
print(info.readonly)       # True
print(info.validator)      # None or callable
```

##### list_properties()

```python
list_properties() -> list
```

Get a list of all property names.

**Returns:**
- List of property names

**Example:**
```python
props = config.list_properties()
# ['host', 'port', 'debug']
```

##### get()

```python
get(name: str, default=None) -> Any
```

Get a property value with optional default.

**Parameters:**
- `name`: Property name
- `default`: Value to return if property doesn't exist

**Returns:**
- Property value or default

**Example:**
```python
host = config.get('host', 'localhost')
missing = config.get('missing', 'default')
```

##### keys()

```python
keys() -> Iterator[str]
```

Return an iterator over property names.

**Example:**
```python
for key in config.keys():
    print(key)
```

##### values()

```python
values() -> Iterator[Any]
```

Return an iterator over property values.

**Example:**
```python
for value in config.values():
    print(value)
```

##### items()

```python
items() -> Iterator[tuple[str, Any]]
```

Return an iterator over (name, value) pairs.

**Example:**
```python
for name, value in config.items():
    print(f"{name} = {value}")
```

#### Properties

##### frozen

```python
frozen: bool
```

Check if configuration is frozen (read-only).

**Example:**
```python
if config.frozen:
    print("Configuration is locked")
```

#### Special Methods

##### `__contains__`

```python
'property_name' in config
```

Check if a property exists.

**Example:**
```python
if 'debug' in config:
    print("Debug property exists")
```

##### `__getattr__` / `__setattr__`

```python
config.property_name
config.property_name = value
```

Get/set property values via attribute access.

**Example:**
```python
host = config.host
config.port = 3000
```

##### `__getitem__` / `__setitem__` / `__delitem__`

```python
config['property_name']
config['property_name'] = value
del config['property_name']
```

Get/set/delete property values via dict-style access.

**Example:**
```python
host = config['host']
config['port'] = 3000
del config['debug']
```

##### `__len__`

```python
len(config)
```

Return number of properties.

**Example:**
```python
count = len(config)
```

##### `__iter__`

```python
for name in config:
    print(name)
```

Iterate over property names.

##### `__str__` / `__repr__`

```python
str(config)
repr(config)
```

String representations.

**Example:**
```python
print(config)  # TyConf(debug=False, host='localhost', port=8080)
print(repr(config))  # <TyConf with 3 properties>
```

##### `__hash__`

TyConf is unhashable (mutable object). Calling `hash(config)` raises `TypeError`.

---

### PropertyDescriptor

Data class containing property metadata.

**Attributes:**
- `name: str` - Property name
- `prop_type: type` - Property type
- `default_value: Any` - Default value
- `readonly: bool` - Whether property is read-only
- `validator: callable | None` - Optional validator function

**Example:**
```python
from tyconf import PropertyDescriptor

descriptor = PropertyDescriptor(
    name="VERSION",
    prop_type=str,
    default_value="1.0.0",
    readonly=True,
    validator=None
)
```

#### Function Validators

```python
def validate_password(value):
    """Validate password strength."""
    if len(value) < 8:
        raise ValueError("must be at least 8 characters")
    if not any(c.isupper() for c in value):
        raise ValueError("must contain uppercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("must contain digit")
    return True

config = TyConf(
    password=(str, "Secret123", validate_password)
)
```

### Validator Behavior

Validators can:

1. **Return `True`** - Validation passes
2. **Return `False`** - Validation fails with generic message
3. **Return `None`** - Treated as success (implicit return)
4. **Raise `ValueError`** - Validation fails with custom message

**Example:**
```python
def my_validator(value):
    if value < 0:
        raise ValueError("must be non-negative")  # Custom message
    return True  # Explicit success

def another_validator(value):
    if value < 0:
        raise ValueError("must be non-negative")
    # Implicit return None - treated as success
```

---

## Type Support

TyConf supports the following types:

### Basic Types

- `str` - String
- `int` - Integer
- `float` - Float
- `bool` - Boolean
- `list` - List
- `dict` - Dictionary
- `tuple` - Tuple
- Any other Python type

### Generic Types (Python 3.9+)

```python
config = TyConf(
    tags=(list[str], []),
    mapping=(dict[str, int], {}),
    coordinates=(tuple[float, float], (0.0, 0.0))
)

config.tags = ["a", "b", "c"]        # OK
config.mapping = {"x": 1, "y": 2}    # OK
config.coordinates = (1.5, 2.5)      # OK
```

### Typing Module Types

#### Optional

```python
from typing import Optional

config = TyConf(
    api_key=(Optional[str], None)
)

config.api_key = "secret"  # OK
config.api_key = None      # OK
config.api_key = 123       # TypeError
```

#### Union

```python
from typing import Union

config = TyConf(
    port=(Union[int, str], 8080)
)

config.port = 3000    # OK (int)
config.port = "auto"  # OK (str)
config.port = 3.14    # TypeError (float)
```

#### Union with Generics

```python
from typing import Union

config = TyConf(
    data=(Union[list[int], str], [])
)

config.data = [1, 2, 3]  # OK (list)
config.data = "text"     # OK (str)
config.data = 123        # TypeError
```

---

## Error Handling

### TypeError

Raised when a value doesn't match the expected type:

```python
config = TyConf(port=(int, 8080))
# config.port = "invalid"  # TypeError: Property 'port': expected int, got str
```

### AttributeError

Raised when:
- Trying to modify a read-only property
- Trying to modify a frozen configuration
- Accessing a non-existent property
- Adding properties to a frozen configuration
- Removing properties from a frozen configuration

```python
# Read-only property
config = TyConf(VERSION=(str, "1.0.0", True))
# config.VERSION = "2.0"  # AttributeError: Property 'VERSION' is read-only

# Frozen configuration
config = TyConf(debug=(bool, True))
config.freeze()
# config.debug = False  # AttributeError: Cannot modify frozen TyConf

# Non-existent property
# config.missing  # AttributeError: TyConf has no property 'missing'
```

### ValueError

Raised when:
- A property definition tuple has the wrong number of elements.
- A property name starts with an underscore (`_`), as this is reserved.
- A validator function returns `False` or raises a `ValueError`.
- Both readonly and validator are specified for the same property.

```python
from tyconf.validators import range

# Invalid name
# config = TyConf(_secret=(str, "value"))  # ValueError: Property name '_secret' is reserved.

# Failed validation
config = TyConf(port=(int, 8080, range(1024, 65535)))
# config.port = 80  # ValueError: Value 80 not in range [1024, 65535]

# Cannot have both readonly and validator
# config = TyConf(port=(int, 8080, True, lambda x: x > 0))  # ValueError
```

### KeyError

Raised when using dict-style access on non-existent properties:

```python
# value = config['missing']  # KeyError: 'missing'
```

---

## Validators Module

TyConf includes a comprehensive set of built-in validators for common validation scenarios. Validators can be imported from `tyconf.validators`.

### Built-in Validators

#### range()

```python
range(min_val, max_val)
```

Validate that a numeric value is within a specified range (inclusive).

**Parameters:**
- `min_val`: Minimum allowed value (inclusive)
- `max_val`: Maximum allowed value (inclusive)

**Example:**
```python
from tyconf import TyConf
from tyconf.validators import range

config = TyConf(
    port=(int, 8080, range(1024, 65535)),
    temperature=(float, 20.0, range(-50.0, 50.0))
)

config.port = 3000       # OK
config.port = 80         # ValueError: Value 80 not in range [1024, 65535]
config.temperature = 25.5  # OK
config.temperature = 100   # ValueError: Value 100 not in range [-50.0, 50.0]
```

#### length()

```python
length(min_len, max_len=None)
```

Validate the length of strings, lists, or other collections.

**Parameters:**
- `min_len`: Minimum length (inclusive)
- `max_len`: Optional maximum length (inclusive). If `None`, only minimum is enforced.

**Example:**
```python
from tyconf.validators import length

config = TyConf(
    username=(str, "admin", length(3, 20)),
    password=(str, "secret123", length(8)),
    tags=(list, [], length(1, 5))
)

config.username = "john"        # OK
config.username = "ab"          # ValueError: Length 2 not in range [3, 20]
config.password = "pass"        # ValueError: Length 4 not in range [8, None]
config.tags = ["python", "config"]  # OK
config.tags = []                # ValueError: Length 0 not in range [1, 5]
```

#### regex()

```python
regex(pattern, flags=0)
```

Validate that a string matches a regular expression pattern.

**Parameters:**
- `pattern`: Regular expression pattern (string or compiled pattern)
- `flags`: Optional regex flags (e.g., `re.IGNORECASE`)

**Example:**
```python
from tyconf.validators import regex
import re

config = TyConf(
    email=(str, "user@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    phone=(str, "555-1234", regex(r'^\d{3}-\d{4}$')),
    code=(str, "ABC123", regex(r'^[A-Z]{3}\d{3}$', re.IGNORECASE))
)

config.email = "test@domain.com"  # OK
config.email = "invalid-email"    # ValueError: Value does not match pattern
config.phone = "555-9999"         # OK
config.phone = "5551234"          # ValueError: Value does not match pattern
```

#### one_of()

```python
one_of(*values)
```

Validate that a value is one of the allowed values.

**Parameters:**
- `*values`: Variable number of allowed values

**Example:**
```python
from tyconf.validators import one_of

config = TyConf(
    environment=(str, "development", one_of("development", "staging", "production")),
    log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    mode=(int, 1, one_of(1, 2, 3))
)

config.environment = "production"  # OK
config.environment = "test"        # ValueError: Value 'test' not in allowed values
config.log_level = "DEBUG"         # OK
config.mode = 2                    # OK
config.mode = 4                    # ValueError: Value 4 not in allowed values
```

#### all_of()

```python
all_of(*validators)
```

Combine multiple validators - all must pass for validation to succeed.

**Parameters:**
- `*validators`: Variable number of validator functions

**Example:**
```python
from tyconf.validators import all_of, length, regex

config = TyConf(
    # Username must be 3-20 chars AND match pattern
    username=(str, "admin", all_of(
        length(3, 20),
        regex(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    )),
    # Password must be 8+ chars AND contain special char
    password=(str, "Secret@123", all_of(
        length(8),
        regex(r'.*[!@#$%^&*].*')
    ))
)

config.username = "john_doe"    # OK (length OK, pattern OK)
config.username = "ab"          # ValueError: Failed length validator
config.username = "123user"     # ValueError: Failed regex validator
```

#### any_of()

```python
any_of(*validators)
```

Alternative validators - at least one must pass for validation to succeed.

**Parameters:**
- `*validators`: Variable number of validator functions

**Example:**
```python
from tyconf.validators import any_of, one_of, range

config = TyConf(
    # Port can be number in range OR special string value
    port=(int, 8080, any_of(
        range(1024, 65535),
        one_of(0, -1)  # Special: 0 = auto, -1 = disabled
    ))
)

config.port = 3000   # OK (in range)
config.port = 0      # OK (special value)
config.port = -1     # OK (special value)
config.port = 80     # ValueError: None of the validators passed
```

#### not_in()

```python
not_in(*values)
```

Validate that a value is NOT one of the disallowed values.

**Parameters:**
- `*values`: Variable number of disallowed values

**Example:**
```python
from tyconf.validators import not_in

config = TyConf(
    username=(str, "admin", not_in("root", "admin", "administrator")),
    port=(int, 8080, not_in(22, 23, 25))  # Reserved ports
)

config.username = "john"    # OK
config.username = "root"    # ValueError: Value 'root' is not allowed
config.port = 3000          # OK
config.port = 22            # ValueError: Value 22 is not allowed
```

### Custom Validators

You can create custom validators as simple lambda functions or full functions.

#### Lambda Validators

For simple validation logic, use lambda functions:

```python
config = TyConf(
    # Positive numbers only
    count=(int, 10, lambda x: x > 0),
    
    # Non-empty strings
    name=(str, "MyApp", lambda x: len(x) > 0),
    
    # Even numbers only
    even_number=(int, 4, lambda x: x % 2 == 0)
)

config.count = 5     # OK
config.count = -1    # ValueError: Validation failed
```

Lambda validators should return `True` if valid, `False` if invalid, or `None` to skip validation.

#### Custom Validator Functions

For complex validation with custom error messages, create validator functions that raise `ValueError`:

```python
def validate_email(value):
    """Validate email address format."""
    if '@' not in value or '.' not in value:
        raise ValueError(f"Invalid email address: {value}")
    return True

def validate_password_strength(value):
    """Validate password meets strength requirements."""
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain uppercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain a number")
    return True

config = TyConf(
    email=(str, "user@example.com", validate_email),
    password=(str, "Secret123", validate_password_strength)
)

# Valid assignments
config.email = "test@domain.com"  # OK
config.password = "MyPass123"     # OK

# Invalid assignments with custom messages
# config.email = "invalid"
# ValueError: Invalid email address: invalid

# config.password = "weak"
# ValueError: Password must be at least 8 characters
```

### Validator Behavior

Validators are callables that are invoked with the value to validate. They can:

1. **Return `True`**: Validation succeeds
2. **Return `False`**: Validation fails with a generic error message
3. **Return `None`**: Skip validation (useful for conditional validation)
4. **Raise `ValueError`**: Validation fails with a custom error message

**Example:**
```python
def conditional_validator(value):
    """Only validate non-None values."""
    if value is None:
        return None  # Skip validation
    if value < 0:
        raise ValueError("Must be non-negative")
    return True
```

### Validation Timing

Validators are called:
1. **During initialization**: When the property is first created
2. **On assignment**: When the property value is changed via attribute or dict-style access
3. **On update**: When the property is modified via the `update()` method

**Example:**
```python
from tyconf.validators import range

# Validation on initialization
config = TyConf(
    port=(int, 8080, range(1024, 65535))  # Validates 8080
)

# Validation on assignment
config.port = 3000  # Validates 3000

# Validation on update
config.update(port=9000)  # Validates 9000
```

### Validators vs Read-Only

Validators and readonly flags are **mutually exclusive** - you cannot have both on the same property:

```python
# ❌ Wrong - cannot have both validator and readonly
# config = TyConf(
#     VERSION=(str, "1.0.0", True, lambda x: len(x) > 0)
# )

# ✅ Correct - choose one
config = TyConf(
    VERSION=(str, "1.0.0", True),           # Read-only
    port=(int, 8080, lambda x: x > 1024)    # Validator
)
```

---

## Version Information

Access version information from the package:

```python
import tyconf

print(tyconf.__version__)    # '1.1.0'
print(tyconf.__author__)     # 'barabasz'
print(tyconf.__license__)    # 'MIT'
print(tyconf.__url__)        # 'https://github.com/barabasz/tyconf'
```
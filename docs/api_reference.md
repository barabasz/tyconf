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
  - `(type, default_value, readonly)` - Read-only property when `readonly=True`
  - `(type, default_value, validator)` - Property with validator when `validator` is callable

**Raises:**
- `TypeError`: If a property definition is not a tuple or list, or if third parameter is neither bool nor callable.
- `ValueError`: If a property definition tuple has the wrong number of elements, if a property name starts with an underscore (`_`), or if validator fails.

**Example:**
```python
from tyconf import TyConf
from tyconf.validators import range

config = TyConf(
    VERSION=(str, "1.0.0", True),              # Read-only
    port=(int, 8080, range(1024, 65535)),      # With validator
    debug=(bool, False)                         # Mutable
)

# This will raise ValueError because the name starts with an underscore
# config = TyConf(_internal=(int, 123))
```

#### Methods

##### add()

```python
add(name: str, prop_type: type, default_value: Any, readonly: bool = False, validator: Optional[Callable] = None)
```

Add a new property to the configuration.

**Parameters:**
- `name`: Property name
- `prop_type`: Expected type (supports `Optional`, `Union`, and generics like `list[str]`)
- `default_value`: Default value for the property
- `readonly`: If `True`, property cannot be modified after creation
- `validator`: Optional callable to validate property values

**Raises:**
- `AttributeError`: If TyConf is frozen or property already exists
- `ValueError`: If the property name is reserved (starts with an underscore `_`) or validator fails
- `TypeError`: If default_value doesn't match prop_type

**Example:**
```python
from tyconf.validators import length

config = TyConf()
config.add('host', str, 'localhost')
config.add('tags', list[str], [])
config.add('VERSION', str, '1.0.0', readonly=True)
config.add('username', str, 'admin', validator=lambda x: len(x) >= 3)
config.add('port', int, 8080, validator=range(1024, 65535))

# This will raise ValueError
# config.add('_secret', str, 'value')
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

##### try_set()

```python
try_set(name: str, value: Any) -> bool
```

Try to set a property value safely without raising exceptions.

Attempts to set the property value. If the assignment fails due to type mismatch, validation error, read-only restriction, or missing property, the method simply returns False instead of raising an exception.

**Parameters:**
- `name`: Property name
- `value`: Value to set

**Returns:**
- `True` if value was set successfully
- `False` if any error occurred (TypeError, ValueError, AttributeError, KeyError)

**Example:**

```python
config = TyConf(port=(int, 8080, range(1024, 65535)))

# Successful update
if config.try_set('port', 3000):
    print("Port updated")

# Failed update (invalid type) - no crash
if not config.try_set('port', "invalid"):
    print("Invalid port type")

# Failed update (validation error) - no crash
config.try_set('port', 80)  # Returns False
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
- `validator: Optional[Callable]` - Validator function (if any)

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

---

## Validators Module

TyConf includes a `validators` module with ready-to-use validators for common validation scenarios.

### Import

```python
from tyconf import validators
# or
from tyconf.validators import range, length, regex, one_of, all_of
```

### Built-in Validators

#### contains()

```python
contains(substring: str, case_sensitive: bool = True) -> Callable
```

Validate that a string contains the specified substring.

**Parameters:**
- `substring`: The text that must be present.
- `case_sensitive`: If `False`, ignores case differences (default: `True`).

**Example:**
```python
from tyconf import TyConf
from tyconf.validators import contains

config = TyConf(
    api_url=(str, "https://api.dev", contains("https://")),
    environment=(str, "PROD", contains("prod", case_sensitive=False))
)
```

#### range()

```python
range(min_val=None, max_val=None) -> Callable
```

Validate that a numeric value is within the specified range.

**Parameters:**
- `min_val`: Minimum allowed value (inclusive). None means no minimum.
- `max_val`: Maximum allowed value (inclusive). None means no maximum.

**Example:**
```python
from tyconf import TyConf
from tyconf.validators import range

config = TyConf(
    port=(int, 8080, range(1024, 65535)),
    percentage=(int, 50, range(0, 100)),
    age=(int, 18, range(min_val=0))  # Only minimum
)
```

#### length()

```python
length(min_len=None, max_len=None) -> Callable
```

Validate that a string or collection has length within the specified range.

**Parameters:**
- `min_len`: Minimum allowed length (inclusive). None means no minimum.
- `max_len`: Maximum allowed length (inclusive). None means no maximum.

**Example:**
```python
from tyconf.validators import length

config = TyConf(
    username=(str, "admin", length(min_len=3, max_len=20)),
    password=(str, "secret", length(min_len=8)),
    tags=(list, [], length(max_len=10))
)
```

#### regex()

```python
regex(pattern: str) -> Callable
```

Validate that a string matches the specified regular expression pattern.

**Parameters:**
- `pattern`: Regular expression pattern to match.

**Example:**
```python
from tyconf.validators import regex

config = TyConf(
    email=(str, "user@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    phone=(str, "+48123456789", regex(r'^\+?[0-9]{9,15}$'))
)
```

#### one_of()

```python
one_of(*allowed_values) -> Callable
```

Validate that a value is one of the allowed values.

**Parameters:**
- `*allowed_values`: Allowed values.

**Example:**
```python
from tyconf.validators import one_of

config = TyConf(
    log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR")),
    environment=(str, "dev", one_of("dev", "staging", "prod"))
)
```

#### all_of()

```python
all_of(*validators) -> Callable
```

Combine multiple validators - all must pass.

**Parameters:**
- `*validators`: Validator functions to combine.

**Example:**
```python
from tyconf.validators import all_of, length, regex

config = TyConf(
    username=(str, "admin", all_of(
        length(min_len=3, max_len=20),
        regex(r'^[a-zA-Z0-9_]+$')
    ))
)
```

#### any_of()

```python
any_of(*validators) -> Callable
```

Combine multiple validators - at least one must pass.

**Parameters:**
- `*validators`: Validator functions to combine.

**Example:**
```python
from tyconf.validators import any_of, regex

config = TyConf(
    contact=(str, "user@example.com", any_of(
        regex(r'^[\w\.-]+@[\w\.-]+\.\w+$'),  # Email
        regex(r'^\+?[0-9]{9,15}$')            # Phone
    ))
)
```

#### not_in()

```python
not_in(*disallowed_values) -> Callable
```

Validate that a value is NOT in the disallowed set.

**Parameters:**
- `*disallowed_values`: Disallowed values.

**Example:**
```python
from tyconf.validators import not_in, all_of, range

config = TyConf(
    port=(int, 8080, all_of(
        range(1024, 65535),
        not_in(3000, 5000, 8000)  # Reserved ports
    ))
)
```

### Custom Validators

You can create custom validators using lambdas or functions:

#### Lambda Validators

```python
config = TyConf(
    percentage=(int, 50, lambda x: 0 <= x <= 100),
    even_number=(int, 10, lambda x: x % 2 == 0)
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
- A validator fails validation.

```python
# Invalid name
# config = TyConf(_secret=(str, "value"))  # ValueError: Property name '_secret' is reserved.

# Validator failure
from tyconf.validators import range
config = TyConf(port=(int, 8080, range(1024, 65535)))
# config.port = 80  # ValueError: Property 'port': must be >= 1024
```

### KeyError

Raised when using dict-style access on non-existent properties:

```python
# value = config['missing']  # KeyError: 'missing'
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
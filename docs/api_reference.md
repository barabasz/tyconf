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

**Raises:**
- `TypeError`: If a property definition is not a tuple or list.
- `ValueError`: If a property definition tuple has the wrong number of elements, or if a property name starts with an underscore (`_`).

**Example:**
```python
config = TyConf(
    VERSION=(str, "1.0.0", True),  # Read-only
    debug=(bool, False)             # Mutable
)

# This will raise ValueError because the name starts with an underscore
# config = TyConf(_internal=(int, 123))
```

#### Methods

##### add()

```python
add(name: str, prop_type: type, default_value: Any, readonly: bool = False)
```

Add a new property to the configuration.

**Parameters:**
- `name`: Property name
- `prop_type`: Expected type (supports `Optional`, `Union`, and generics like `list[str]`)
- `default_value`: Default value for the property
- `readonly`: If `True`, property cannot be modified after creation

**Raises:**
- `AttributeError`: If TyConf is frozen or property already exists
- `ValueError`: If the property name is reserved (starts with an underscore `_`)
- `TypeError`: If default_value doesn't match prop_type

**Example:**
```python
config = TyConf()
config.add('host', str, 'localhost')
config.add('tags', list[str], [])
config.add('VERSION', str, '1.0.0', readonly=True)

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
- **Property types and readonly flags**

The copy is always unfrozen, even if the original is frozen.

**Returns:**
- New `TyConf` instance with same properties and current values

**Example:**
```python
config = TyConf(debug=(bool, True), port=(int, 8080))

# Modify values
config.debug = False
config.port = 3000
config.freeze()

# Create copy - preserves current values
backup = config.copy()
backup.frozen        # False (copy is unfrozen)
backup.debug         # False (current value)
backup.port          # 3000 (current value)

# Reset restores ORIGINAL defaults, not copied values
backup.reset()
backup.debug         # True (original default)
backup.port          # 8080 (original default)
```

**Important:** The copy preserves original default values, ensuring that `reset()` works correctly even on modified configurations.

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

**Example:**
```python
from tyconf import PropertyDescriptor

descriptor = PropertyDescriptor(
    name="VERSION",
    prop_type=str,
    default_value="1.0.0",
    readonly=True
)
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

```python
# Invalid name
# config = TyConf(_secret=(str, "value"))  # ValueError: Property name '_secret' is reserved.
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

print(tyconf.__version__)    # '1.0.1'
print(tyconf.__author__)     # 'barabasz'
print(tyconf.__license__)    # 'MIT'
print(tyconf.__url__)        # 'https://github.com/barabasz/tyconf'
```
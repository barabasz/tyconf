# TyConf

**TyConf** ≡ **Ty**ped **Conf**ig - a type-safe configuration management library for Python with runtime validation.

## What is TyConf?

TyConf is a modern Python 3.13+ library that makes managing application configuration simple, safe, and intuitive. It provides runtime type validation, value validation, read-only properties, and freeze/unfreeze capabilities to help you build robust applications.

## Quick Start

```python
from tyconf import TyConf
from tyconf.validators import range

# Create configuration with type-safe properties and validators
config = TyConf(
    host=(str, "localhost"),               # Mutable string
    debug=(bool, True),                    # Mutable boolean
    port=(int, 8080, range(1024, 65535)),  # Validated mutable range
    users=(list, ["admin", "root"], True)  # Immutable list
)

# Access values easily
print(config.host)       # 'localhost'
config.port = 3000       # Type-checked and range-validated automatically
config.port = "3000"     # Rises TypeError: Property 'port': expected int, got str
config.users = ["guest"] # Rises AttributeError: Property 'users' is read-only
```

## Serialization

TyConf supports exporting and importing configurations in multiple formats:

```python
from tyconf import TyConf

config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, True)
)

# Export to JSON (with full metadata)
config.to_json('config.json')

# Export to JSON (values only)
config.to_json('values.json', values_only=True)

# Export to TOML (requires: pip install tyconf[toml])
config.to_toml('config.toml')

# Import from JSON
config = TyConf.from_json('config.json')

# Import from TOML (built-in via tomllib)
config = TyConf.from_toml('config.toml')

# Load from environment variables
config = TyConf.from_env(prefix='APP_', schema={
    'host': str,
    'port': int,
    'debug': bool
})

# Merge configurations
config.load_json('overrides.json')  # Merge JSON into existing config
config.load_env(prefix='APP_')      # Merge environment variables
```

## Key Features

✅ **Type Safety** - Runtime type validation with support for `Optional` and `Union` types  
✅ **Value Validation** - Built-in validators (range, length, regex, etc.) and custom validation functions  
✅ **Read-Only Properties** - Protect critical configuration from accidental changes  
✅ **Freeze/Unfreeze** - Lock entire configuration to prevent modifications  
✅ **Serialization** - Export/import configurations to JSON, TOML, and environment variables  
✅ **Intuitive API** - Both attribute (`config.host`) and dict-style (`config['host']`) access  
✅ **Copy & Reset** - Easily duplicate or restore default configurations  
✅ **Zero Dependencies** - Pure Python with no external requirements (TOML write requires optional dependency)  

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

## Documentation

- **[User Guide](https://github.com/barabasz/tyconf/blob/main/docs/user_guide.md)** - Comprehensive guide with all features
- **[API Reference](https://github.com/barabasz/tyconf/blob/main/docs/api_reference.md)** - Complete API documentation
- **[Best Practices](https://github.com/barabasz/tyconf/blob/main/docs/best_practices.md)** - Tips for effective usage

## Examples

See the [examples/](https://github.com/barabasz/tyconf/tree/main/examples) directory for complete examples:

- **[basic_usage.py](https://github.com/barabasz/tyconf/blob/main/examples/basic_usage.py)** - Getting started
- **[advanced_usage.py](https://github.com/barabasz/tyconf/blob/main/examples/advanced_usage.py)** - Advanced features
- **[real_world_app.py](https://github.com/barabasz/tyconf/blob/main/examples/real_world_app.py)** - Real-world application configuration
- **[validation_examples.py](https://github.com/barabasz/tyconf/blob/main/examples/validation_examples.py)** - Value validation examples

## License

MIT License - see [LICENSE](https://github.com/barabasz/tyconf/blob/main/LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **GitHub**: https://github.com/barabasz/tyconf
- **Issues**: https://github.com/barabasz/tyconf/issues

# TyConf

**TyConf** ≡ **Ty**ped **Conf**ig - A type-safe configuration management library for Python with runtime validation.

## What is TyConf?

TyConf is a modern Python library that makes managing application configuration simple, safe, and intuitive. It provides runtime type validation, read-only properties, and freeze/unfreeze capabilities to help you build robust applications.

## Quick Start

```python
from tyconf import TyConf
from tyconf.validators import range

# Create configuration with type-safe properties and validation
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080, range(1024, 65535)),  # Validated range
    debug=(bool, True)
)

# Access values easily
print(config.host)      # 'localhost'
config.port = 3000      # Type-checked and validated automatically
# config.port = 80      # ValueError: Value 80 not in range [1024, 65535]
```

## Key Features

✅ **Type Safety** - Runtime type validation with support for `Optional` and `Union` types  
✅ **Value Validation** - Built-in and custom validators to enforce constraints (ranges, patterns, etc.)  
✅ **Read-Only Properties** - Protect critical configuration from accidental changes  
✅ **Freeze/Unfreeze** - Lock entire configuration to prevent modifications  
✅ **Intuitive API** - Both attribute (`config.host`) and dict-style (`config['host']`) access  
✅ **Copy & Reset** - Easily duplicate or restore default configurations  
✅ **Zero Dependencies** - Pure Python with no external requirements  

## Installation

```bash
pip install tyconf
```

## Validation Examples

Ensure values meet your requirements with validators:

```python
from tyconf import TyConf
from tyconf.validators import range, length, regex, one_of

config = TyConf(
    # Numeric ranges
    port=(int, 8080, range(1024, 65535)),
    
    # String length
    username=(str, "admin", length(3, 20)),
    
    # Pattern matching
    email=(str, "user@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    
    # Allowed values
    environment=(str, "dev", one_of("dev", "staging", "production")),
    
    # Custom validators
    password=(str, "Secret123", lambda x: len(x) >= 8)
)

# All assignments are automatically validated
config.port = 3000                  # ✓ OK
# config.port = 80                  # ✗ ValueError: not in range
config.environment = "production"   # ✓ OK
# config.environment = "test"       # ✗ ValueError: not in allowed values
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

## License

MIT License - see [LICENSE](https://github.com/barabasz/tyconf/blob/main/LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **GitHub**: https://github.com/barabasz/tyconf
- **Issues**: https://github.com/barabasz/tyconf/issues
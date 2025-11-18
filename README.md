# TyConf

**TyConf** ≡ **Ty**ped **Conf**ig - A type-safe configuration management library for Python with runtime validation.

## What is TyConf?

TyConf is a modern Python library that makes managing application configuration simple, safe, and intuitive. It provides runtime type validation, value validation, read-only properties, and freeze/unfreeze capabilities to help you build robust applications.

## Quick Start

```python
from tyconf import TyConf
from tyconf.validators import range

# Create configuration with type-safe properties and validators
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080, range(1024, 65535)),  # Validated range
    debug=(bool, True)
)

# Access values easily
print(config.host)      # 'localhost'
config.port = 3000      # Type-checked and range-validated automatically
```

## Key Features

✅ **Type Safety** - Runtime type validation with support for `Optional` and `Union` types
✅ **Value Validation** - Built-in validators (range, length, regex, etc.) and custom validation functions
✅ **Read-Only Properties** - Protect critical configuration from accidental changes
✅ **Freeze/Unfreeze** - Lock entire configuration to prevent modifications
✅ **Intuitive API** - Both attribute (`config.host`) and dict-style (`config['host']`) access
✅ **Copy & Reset** - Easily duplicate or restore default configurations
✅ **Zero Dependencies** - Pure Python with no external requirements

## Installation

```bash
pip install tyconf
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
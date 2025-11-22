# TyConf Best Practices

Guidelines for using TyConf effectively in your applications.

## Table of Contents

1. [Configuration Organization](#configuration-organization)
2. [Type Safety](#type-safety)
3. [Read-Only Properties](#read-only-properties)
4. [Freezing Configuration](#freezing-configuration)
5. [Environment Variables](#environment-variables)
6. [Testing](#testing)
7. [Configuration Serialization](#configuration-serialization)
8. [Error Handling](#error-handling)
9. [Performance](#performance)
10. [Common Patterns](#common-patterns)

---

## Configuration Organization

### Separate Concerns

Organize configuration into logical groups:

```python
from tyconf import TyConf

# Good: Separate configurations for different concerns
app_config = TyConf(
    APP_NAME=(str, "MyApp", True),
    VERSION=(str, "1.0.0", True)
)

server_config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    workers=(int, 4)
)

db_config = TyConf(
    database_url=(Optional[str], None),
    pool_size=(int, 10),
    timeout=(int, 30)
)
```

### Use Descriptive Names

Choose clear, descriptive property names:

```python
# Good
config = TyConf(
    max_upload_size_mb=(int, 10),
    session_timeout_seconds=(int, 3600),
    enable_debug_mode=(bool, False)
)

# Avoid
config = TyConf(
    max=(int, 10),
    timeout=(int, 3600),
    debug=(bool, False)
)
```

### Follow Naming Conventions

- Use `UPPER_CASE` for read-only constants
- Use `snake_case` for mutable settings

```python
config = TyConf(
    # Constants (read-only)
    APP_NAME=(str, "WebAPI", True),
    VERSION=(str, "1.0.0", True),
    MAX_UPLOAD_SIZE=(int, 10485760, True),
    
    # Settings (mutable)
    debug_mode=(bool, False),
    log_level=(str, "INFO"),
    cache_enabled=(bool, True)
)
```

### Reserved Names

Property names starting with underscore (`_`) are reserved for internal use and cannot be used:

```python
# ❌ Wrong - underscore prefix is reserved
config = TyConf(_private=(str, "value"))  # Will not work as expected

# ✅ Correct - use regular names
config = TyConf(private=(str, "value"))
```

---

## Type Safety

### Be Specific with Types

Use the most specific type possible:

```python
# Good: Specific types
config = TyConf(
    port=(int, 8080),
    timeout=(float, 30.5),
    enabled=(bool, True)
)

# Avoid: Generic types when specific ones are known
from typing import Any
config = TyConf(
    port=(Any, 8080),  # Don't do this
)
```

### Use Optional for Nullable Values

Explicitly mark properties that can be `None`:

```python
from typing import Optional

config = TyConf(
    # Good: Optional for nullable values
    api_key=(Optional[str], None),
    database_url=(Optional[str], None),
    
    # Good: Non-optional for required values
    app_name=(str, "MyApp"),
    port=(int, 8080)
)
```

### Use Union for Multi-Type Properties

When a property legitimately accepts multiple types:

```python
from typing import Union

config = TyConf(
    # Valid use case: port can be number or "auto"
    port=(Union[int, str], 8080),
    
    # Valid use case: workers can be number or "max"
    workers=(Union[int, str], 4)
)

# Then use it appropriately
config.port = 3000
config.port = "auto"
```

---

## Read-Only Properties

### Mark Constants as Read-Only

Always make unchangeable values read-only:

```python
config = TyConf(
    # Read-only constants
    VERSION=(str, "1.0.0", True),
    APP_NAME=(str, "WebAPI", True),
    ENVIRONMENT=(str, os.getenv('ENV', 'prod'), True),
    MAX_UPLOAD_SIZE=(int, 10 * 1024 * 1024, True),
    
    # Mutable settings
    debug=(bool, False),
    port=(int, 8080)
)
```

### Benefits of Read-Only Properties

1. **Prevents Bugs**: Can't accidentally change critical values
2. **Self-Documenting**: Clear which values are constants
3. **Thread-Safe**: Safe to read from multiple threads
4. **Deployment Safety**: Version/environment can't be changed at runtime

---

## Freezing Configuration

### Freeze After Loading

Freeze configuration after loading from environment to prevent runtime changes:

```python
# Load configuration
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080)
)

# Override from environment
config.port = int(os.getenv('PORT', '8080'))

# Freeze before starting app
config.freeze()

# Now safe to use in production
start_application(config)
```

### When to Freeze

✅ **Do freeze:**
- Production configurations after validation
- Shared configurations in multi-threaded apps
- Test fixtures to ensure consistency
- After loading all environment overrides

❌ **Don't freeze:**
- Development configurations that need hot-reload
- Configurations that need runtime updates
- During initialization before all values are set

### Temporary Unfreeze Pattern

If you need to modify a frozen config temporarily:

```python
def update_config_safely(config, **updates):
    """Safely update frozen config."""
    was_frozen = config.frozen
    
    if was_frozen:
        config.unfreeze()
    
    try:
        config.update(**updates)
    finally:
        if was_frozen:
            config.freeze()
```

---

## Environment Variables

### Override Pattern

Use TyConf defaults with environment overrides:

```python
import os
from typing import Optional

# Define with sensible defaults
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080),
    debug=(bool, False),
    database_url=(Optional[str], None)
)

# Override from environment
if os.getenv('HOST'):
    config.host = os.getenv('HOST')

if os.getenv('PORT'):
    config.port = int(os.getenv('PORT'))

if os.getenv('DEBUG'):
    config.debug = os.getenv('DEBUG').lower() == 'true'

if os.getenv('DATABASE_URL'):
    config.database_url = os.getenv('DATABASE_URL')
```

### Environment-Based Defaults

Set defaults based on environment:

```python
import os

env = os.getenv('ENV', 'development')

# Different defaults per environment
config = TyConf(
    ENVIRONMENT=(str, env, True),
    debug=(bool, env == 'development'),
    log_level=(str, 'DEBUG' if env == 'development' else 'INFO'),
    workers=(int, 1 if env == 'development' else 4)
)
```

---

## Testing

### Use Copy for Test Isolation

Create isolated copies for each test:

```python
import pytest

@pytest.fixture
def base_config():
    """Base configuration for tests."""
    return TyConf(
        debug=(bool, False),
        timeout=(int, 30)
    )

def test_with_debug(base_config):
    """Test with debug enabled."""
    config = base_config.copy()
    config.debug = True
    
    # Test doesn't affect other tests
    assert config.debug is True

def test_with_timeout(base_config):
    """Test with custom timeout."""
    config = base_config.copy()
    config.timeout = 60
    
    # Independent from other tests
    assert config.timeout == 60
```

### Test Configuration Validation

Write tests for your configuration:

```python
def test_config_validation():
    """Ensure configuration is valid."""
    config = create_app_config()
    
    # Test types
    assert isinstance(config.port, int)
    assert isinstance(config.host, str)
    
    # Test ranges
    assert 1024 <= config.port <= 65535
    
    # Test read-only
    assert config.get_property_info('VERSION').readonly
    
    # Test can freeze
    config.freeze()
    assert config.frozen
```

---

## Configuration Serialization

### When to Use Values-Only vs Full Metadata

Choose the appropriate export format based on your use case:

#### Use Full Metadata When:

```python
# Application state snapshots
config.to_json('snapshot.json')  # Preserves everything

# Configuration backups
config.to_json('backup.json')

# Sharing between TyConf applications
config.to_toml('shared-config.toml')
```

**Benefits:**
- Complete state preservation
- Type validation on reload
- Maintains readonly flags
- Preserves default values for reset
- Can fully reconstruct configuration

#### Use Values-Only When:

```python
# Configuration overrides
config.to_json('overrides.json', values_only=True)

# External tool integration
config.to_toml('settings.toml', values_only=True)

# Manual editing required
config.to_json('editable-config.json', values_only=True)
```

**Benefits:**
- Simpler, more readable format
- Compatible with non-TyConf tools
- Easier to edit manually
- Smaller file size
- Standard JSON/TOML format

### Handling Validators

Validators cannot be serialized. Use one of these patterns:

#### Pattern 1: Define Validators in Code

```python
# Store values only
config.to_json('config.json', values_only=True)

# Define validators in application
def create_config():
    """Create configuration with validators."""
    config = TyConf(
        host=(str, "localhost"),
        port=(int, 8080, range(1024, 65535)),  # Validator in code
        timeout=(int, 30, lambda x: x > 0)
    )
    
    # Load values from file
    config.load_json('config.json')
    
    return config
```

#### Pattern 2: Re-add Validators After Loading

```python
from tyconf.validators import range, length

# Load configuration
config = TyConf.from_json('config.json')

# Re-add validators for critical properties
port_value = config.port
config.remove('port')
config.add('port', int, port_value, validator=range(1024, 65535))

username_value = config.username
config.remove('username')
config.add('username', str, username_value, validator=length(min_len=3))
```

#### Pattern 3: Validation Layer

```python
def validate_config(config):
    """Separate validation layer."""
    from tyconf.validators import range, regex
    
    # Validate port
    if not (1024 <= config.port <= 65535):
        raise ValueError(f"Invalid port: {config.port}")
    
    # Validate email
    if not regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')(config.email):
        raise ValueError(f"Invalid email: {config.email}")
    
    return True

# Load and validate
config = TyConf.from_json('config.json')
validate_config(config)
```

### Loading Configurations in Production

#### Recommended Loading Order

```python
import os
from tyconf import TyConf

def load_production_config():
    """Load configuration with proper precedence."""
    
    # 1. Start with defaults in code
    config = TyConf(
        host=(str, "localhost"),
        port=(int, 8080, range(1024, 65535)),
        workers=(int, 4, lambda x: x > 0),
        debug=(bool, False),
        log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR"))
    )
    
    # 2. Load base configuration file (optional)
    if os.path.exists('/etc/myapp/config.json'):
        config.load_json('/etc/myapp/config.json')
    
    # 3. Load environment-specific config (optional)
    env = os.getenv('ENV', 'production')
    env_config = f'/etc/myapp/config.{env}.json'
    if os.path.exists(env_config):
        config.load_json(env_config)
    
    # 4. Override with environment variables (highest priority)
    config.load_env(prefix='MYAPP_')
    
    # 5. Validate and freeze
    validate_config(config)
    config.freeze()
    
    return config
```

#### Precedence Strategy

Use this precedence order (later overrides earlier):
1. **Code defaults** - Base configuration in source code
2. **Base config file** - Shared settings (e.g., `/etc/myapp/config.json`)
3. **Environment config** - Environment-specific (e.g., `config.production.json`)
4. **Environment variables** - Runtime overrides (highest priority)

### Environment Variable Patterns

#### Naming Convention

Use consistent naming for environment variables:

```python
# Good: Clear prefix and structure
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=5432
APP_CACHE_ENABLED=true
APP_CACHE_TTL=3600

# Load with prefix
config = TyConf.from_env(
    prefix='APP_',
    schema={
        'database_host': str,
        'database_port': int,
        'cache_enabled': bool,
        'cache_ttl': int
    }
)
```

#### Boolean Environment Variables

Handle boolean values consistently:

```python
import os

# These all evaluate to True
os.environ['APP_DEBUG'] = 'true'
os.environ['APP_DEBUG'] = 'True'
os.environ['APP_DEBUG'] = 'yes'
os.environ['APP_DEBUG'] = '1'

# These all evaluate to False
os.environ['APP_DEBUG'] = 'false'
os.environ['APP_DEBUG'] = 'False'
os.environ['APP_DEBUG'] = 'no'
os.environ['APP_DEBUG'] = '0'
os.environ['APP_DEBUG'] = ''

config = TyConf.from_env(
    prefix='APP_',
    schema={'debug': bool}
)
```

#### Complex Types in Environment

For complex types, use JSON format:

```python
import os

# List in environment variable
os.environ['APP_ALLOWED_HOSTS'] = '["example.com", "www.example.com"]'

# Dictionary in environment variable
os.environ['APP_DATABASE'] = '{"host": "localhost", "port": 5432}'

config = TyConf.from_env(
    prefix='APP_',
    schema={
        'allowed_hosts': list,
        'database': dict
    }
)

print(config.allowed_hosts)  # ['example.com', 'www.example.com']
print(config.database)       # {'host': 'localhost', 'port': 5432}
```

### Security Considerations

#### Don't Commit Secrets

**❌ Wrong:**
```python
# config.json (committed to git)
{
    "database_password": "secret123",  # NEVER DO THIS
    "api_key": "key_abc123"
}
```

**✅ Correct:**
```python
# config.json (committed to git) - no secrets
{
    "database_host": "localhost",
    "database_port": 5432
}

# Secrets from environment only
os.environ['APP_DATABASE_PASSWORD'] = 'secret123'
os.environ['APP_API_KEY'] = 'key_abc123'

config = TyConf.from_json('config.json')
config.load_env(prefix='APP_')  # Adds secrets at runtime
```

#### Separate Public and Private Config

```python
# public-config.json - Safe to commit
{
    "host": "localhost",
    "port": 8080,
    "workers": 4
}

# Load public config
config = TyConf.from_json('public-config.json')

# Add secrets from environment (never committed)
config.add('database_password', str, os.getenv('DB_PASSWORD', ''))
config.add('api_key', str, os.getenv('API_KEY', ''))

# Freeze to prevent accidental exposure
config.freeze()
```

#### Validate Before Using

```python
def load_secure_config():
    """Load config with security validation."""
    config = TyConf.from_json('config.json')
    config.load_env(prefix='APP_')
    
    # Validate required secrets are present
    required_secrets = ['database_password', 'api_key', 'jwt_secret']
    for secret in required_secrets:
        if not config.get(secret):
            raise ValueError(f"Required secret '{secret}' is missing")
    
    # Validate no secrets in debug mode
    if config.debug and config.get('database_password'):
        raise ValueError("Cannot run in debug mode with real credentials")
    
    config.freeze()
    return config
```

#### Use .gitignore

```gitignore
# .gitignore
# Never commit these files
config.local.json
config.production.json
.env
secrets.json
*.secret.toml
```

#### Audit Configuration Files

```python
def audit_config_file(path):
    """Check config file for potential secrets."""
    import re
    
    with open(path, 'r') as f:
        content = f.read()
    
    # Patterns that might indicate secrets
    danger_patterns = [
        r'password\s*[:=]',
        r'secret\s*[:=]',
        r'token\s*[:=]',
        r'key\s*[:=]',
        r'api_key\s*[:=]'
    ]
    
    for pattern in danger_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"WARNING: Potential secret in {path}: {pattern}")
```

### Production Checklist

Before deploying with serialized configs:

- ✅ Use values-only format for manually edited configs
- ✅ Define validators in code, not in config files
- ✅ Load configs in correct precedence order
- ✅ Never commit secrets to JSON/TOML files
- ✅ Use environment variables for secrets
- ✅ Validate configuration after loading
- ✅ Freeze configuration before use
- ✅ Add .gitignore entries for secret config files
- ✅ Use consistent environment variable naming
- ✅ Document required environment variables

---

## Error Handling

### Validate Early

Validate configuration at startup:

```python
def validate_config(config):
    """Validate configuration before starting app."""
    errors = []
    
    # Check required values
    if not config.database_url:
        errors.append("DATABASE_URL is required")
    
    # Check ranges
    if not (1024 <= config.port <= 65535):
        errors.append(f"Port {config.port} out of range")
    
    # Check dependencies
    if config.enable_cache and not config.redis_url:
        errors.append("Cache requires REDIS_URL")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(errors))

# Usage
config = load_config()
validate_config(config)
config.freeze()
```

### Handle Type Errors Gracefully

Provide helpful error messages when loading from environment:

```python
def load_int_from_env(key, default):
    """Load integer from environment with error handling."""
    value = os.getenv(key)
    if value is None:
        return default
    
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable {key}='{value}' is not a valid integer"
        )

# Usage
config = TyConf(
    port=(int, load_int_from_env('PORT', 8080)),
    workers=(int, load_int_from_env('WORKERS', 4))
)
```

---

## Performance

### Configuration is Lightweight

TyConf has minimal overhead:

```python
# Creating configs is fast
config = TyConf(
    host=(str, "localhost"),
    port=(int, 8080)
)

# Accessing values is fast (direct dict lookup)
host = config.host        # Fast
port = config['port']     # Fast
```

### Freeze for Multi-Threading

Frozen configurations are safe to share across threads:

```python
# Main thread
config = create_config()
config.freeze()  # Now thread-safe for reads

# Worker threads can safely read
def worker():
    host = config.host
    port = config.port
    # Safe - config is frozen
```

### Don't Re-Validate

Type validation happens on assignment, not access:

```python
config = TyConf(port=(int, 8080))

# Validation happens here
config.port = 3000  # Validates type

# No validation here (fast)
for i in range(1000000):
    port = config.port  # Just a dict lookup
```

---

## Common Patterns

### Factory Pattern

Create configurations with factory functions:

```python
def create_dev_config():
    """Create development configuration."""
    return TyConf(
        ENVIRONMENT=(str, "development", True),
        debug=(bool, True),
        log_level=(str, "DEBUG"),
        workers=(int, 1)
    )

def create_prod_config():
    """Create production configuration."""
    return TyConf(
        ENVIRONMENT=(str, "production", True),
        debug=(bool, False),
        log_level=(str, "INFO"),
        workers=(int, 4)
    )

# Usage
env = os.getenv('ENV', 'development')
if env == 'production':
    config = create_prod_config()
else:
    config = create_dev_config()
```

### Builder Pattern

Build configuration step by step:

```python
def build_config():
    """Build configuration from multiple sources."""
    # Start with defaults
    config = TyConf(
        host=(str, "localhost"),
        port=(int, 8080),
        debug=(bool, False)
    )
    
    # Load from file
    if os.path.exists('config.json'):
        settings = load_json('config.json')
        config.update(**settings)
    
    # Override from environment
    if os.getenv('PORT'):
        config.port = int(os.getenv('PORT'))
    
    # Freeze final config
    config.freeze()
    
    return config
```

### Singleton Pattern

Share a single configuration instance:

```python
# config.py
_config = None

def get_config():
    """Get application configuration (singleton)."""
    global _config
    if _config is None:
        _config = TyConf(
            host=(str, "localhost"),
            port=(int, 8080)
        )
        _config.freeze()
    return _config

# Usage in other modules
from config import get_config

config = get_config()
print(config.host)
```

---

## Summary

**Do:**
- ✅ Use specific types (int, str, bool)
- ✅ Mark constants as read-only
- ✅ Freeze production configs
- ✅ Validate configuration at startup
- ✅ Use descriptive names
- ✅ Use Optional for nullable values

**Don't:**
- ❌ Use generic Any type
- ❌ Modify frozen configs
- ❌ Use mutable defaults (lists, dicts) across instances
- ❌ Skip validation
- ❌ Freeze during initialization

Following these practices will help you build robust, maintainable applications with TyConf!
# TyConf Best Practices

Guidelines for using TyConf effectively in your applications.

## Table of Contents

1. [Configuration Organization](#configuration-organization)
2. [Type Safety](#type-safety)
3. [Read-Only Properties](#read-only-properties)
4. [Freezing Configuration](#freezing-configuration)
5. [Environment Variables](#environment-variables)
6. [Testing](#testing)
7. [Error Handling](#error-handling)
8. [Performance](#performance)
9. [Common Patterns](#common-patterns)

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

## Value Validation

Beyond type validation, TyConf allows you to validate property values using validators. This ensures that values meet specific business rules and constraints.

### Choose the Right Validator

Use built-in validators for common scenarios:

```python
from tyconf import TyConf
from tyconf.validators import range, length, regex, one_of

config = TyConf(
    # Numeric ranges
    port=(int, 8080, range(1024, 65535)),
    percentage=(int, 50, range(0, 100)),
    
    # String/collection lengths
    username=(str, "admin", length(3, 20)),
    tags=(list, [], length(1, 10)),
    
    # Pattern matching
    email=(str, "user@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    
    # Allowed values
    environment=(str, "dev", one_of("dev", "staging", "prod"))
)
```

### Lambda for Simple Validation

Use lambda functions for straightforward validation logic:

```python
config = TyConf(
    # Good: Simple, clear lambda validators
    port=(int, 8080, lambda x: x > 1024),
    username=(str, "admin", lambda x: len(x) > 0),
    count=(int, 10, lambda x: x >= 0),
    
    # Avoid: Complex logic in lambdas (use functions instead)
    # password=(str, "pass", lambda x: len(x) >= 8 and any(c.isupper() for c in x) and any(c.isdigit() for c in x))
)
```

**Best Practices:**
- ✅ Use lambdas for single-condition validation
- ✅ Keep lambdas simple and readable
- ❌ Avoid complex logic in lambdas
- ❌ Don't use lambdas when you need custom error messages

### Custom Functions for Complex Validation

Create validator functions for complex logic or custom error messages:

```python
def validate_password_strength(value):
    """Validate password meets security requirements."""
    errors = []
    if len(value) < 8:
        errors.append("at least 8 characters")
    if not any(c.isupper() for c in value):
        errors.append("an uppercase letter")
    if not any(c.isdigit() for c in value):
        errors.append("a number")
    if not any(c in '!@#$%^&*' for c in value):
        errors.append("a special character")
    
    if errors:
        raise ValueError(f"Password must contain {', '.join(errors)}")
    return True

def validate_email_domain(value):
    """Ensure email is from allowed domain."""
    allowed_domains = ['company.com', 'partner.com']
    domain = value.split('@')[1] if '@' in value else ''
    if domain not in allowed_domains:
        raise ValueError(f"Email domain must be one of: {', '.join(allowed_domains)}")
    return True

config = TyConf(
    password=(str, "Secret123!", validate_password_strength),
    email=(str, "user@company.com", validate_email_domain)
)

# Clear error messages help users fix issues
# config.password = "weak"
# ValueError: Password must contain at least 8 characters, an uppercase letter, a number, a special character
```

**Best Practices:**
- ✅ Provide clear, actionable error messages
- ✅ Validate multiple conditions in one function
- ✅ Document what the validator checks
- ✅ Return `True` on success, raise `ValueError` on failure

### Combine Validators

Use `all_of()` and `any_of()` to combine validators:

```python
from tyconf.validators import all_of, any_of, length, regex, range, one_of

config = TyConf(
    # All validators must pass
    username=(str, "admin", all_of(
        length(3, 20),
        regex(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    )),
    
    # At least one validator must pass
    port=(int, 8080, any_of(
        range(1024, 65535),
        one_of(0, -1)  # Special values: 0=auto, -1=disabled
    ))
)
```

**Best Practices:**
- ✅ Use `all_of()` when multiple conditions must be met
- ✅ Use `any_of()` for alternative valid values
- ✅ Combine built-in validators before writing custom ones
- ✅ Order validators from fastest to slowest (fail fast)

### Validation Best Practices

1. **Validate at Creation**: Set up validation when defining properties
```python
# Good: Validation defined upfront
config = TyConf(
    port=(int, 8080, range(1024, 65535))
)

# Avoid: No validation, rely on manual checks
config = TyConf(port=(int, 8080))
if not (1024 <= config.port <= 65535):
    raise ValueError("Invalid port")
```

2. **Use Appropriate Validators**: Match validator to data type
```python
# Good: Right validator for the job
config = TyConf(
    port=(int, 8080, range(1024, 65535)),      # Numeric range
    username=(str, "admin", length(3, 20)),     # String length
    env=(str, "dev", one_of("dev", "prod"))     # Allowed values
)
```

3. **Fail Fast with Clear Messages**: Use custom validators for better errors
```python
# Good: Clear error message
def validate_api_key(value):
    if not value.startswith('sk_'):
        raise ValueError("API key must start with 'sk_'")
    if len(value) != 32:
        raise ValueError("API key must be exactly 32 characters")
    return True

config = TyConf(
    api_key=(str, "sk_" + "0"*29, validate_api_key)
)
```

4. **Don't Over-Validate**: Balance safety with flexibility
```python
# Good: Reasonable validation
config = TyConf(
    timeout=(int, 30, range(1, 3600))
)

# Over-validation: Too restrictive
# config = TyConf(
#     timeout=(int, 30, one_of(10, 20, 30, 60))  # What if user needs 45?
# )
```

5. **Document Validation Rules**: Help users understand requirements
```python
def validate_cron_expression(value):
    """
    Validate cron expression format.
    
    Format: 'minute hour day month weekday'
    Example: '0 2 * * *' (runs at 2:00 AM daily)
    """
    parts = value.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have 5 fields: minute hour day month weekday")
    # Additional validation...
    return True
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
    
    # Mutable settings (optionally with validators)
    debug=(bool, False),
    port=(int, 8080, range(1024, 65535))
)
```

### Benefits of Read-Only Properties

1. **Prevents Bugs**: Can't accidentally change critical values
2. **Self-Documenting**: Clear which values are constants
3. **Thread-Safe**: Safe to read from multiple threads
4. **Deployment Safety**: Version/environment can't be changed at runtime

### Read-Only vs Validators

**Important:** Read-only and validators are mutually exclusive. The third parameter in a property definition is auto-detected:
- If `bool` → readonly flag
- If `callable` → validator function

```python
# ✅ Correct: Use readonly OR validator
config = TyConf(
    VERSION=(str, "1.0.0", True),              # Read-only (bool)
    port=(int, 8080, range(1024, 65535)),      # Validator (callable)
    debug=(bool, False)                        # Neither (mutable)
)

# ❌ Wrong: Cannot have both
# You can't have both readonly and validator on the same property
# The third parameter determines which one you get
```

**When to use each:**
- Use **readonly** for constants that never change (version, app name, etc.)
- Use **validators** for values that can change but must meet constraints (port, email, etc.)

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
from tyconf.validators import range, one_of

@pytest.fixture
def base_config():
    """Base configuration for tests."""
    return TyConf(
        debug=(bool, False),
        timeout=(int, 30, range(1, 300)),
        environment=(str, "test", one_of("dev", "test", "prod"))
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
from tyconf.validators import range

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

def test_validator_enforcement():
    """Test that validators are enforced."""
    config = TyConf(
        port=(int, 8080, range(1024, 65535))
    )
    
    # Valid value should work
    config.port = 3000
    assert config.port == 3000
    
    # Invalid value should raise ValueError
    with pytest.raises(ValueError, match="not in range"):
        config.port = 80
```

### Test Custom Validators

Test your custom validator functions:

```python
def test_password_validator():
    """Test password strength validator."""
    def validate_password(value):
        if len(value) < 8:
            raise ValueError("Password too short")
        if not any(c.isupper() for c in value):
            raise ValueError("Password needs uppercase")
        return True
    
    config = TyConf(
        password=(str, "Secret123", validate_password)
    )
    
    # Valid password
    config.password = "StrongPass1"
    assert config.password == "StrongPass1"
    
    # Too short
    with pytest.raises(ValueError, match="too short"):
        config.password = "short"
    
    # No uppercase
    with pytest.raises(ValueError, match="uppercase"):
        config.password = "lowercase123"

def test_validator_on_initialization():
    """Test that validators run on initialization."""
    from tyconf.validators import range
    
    # Should work with valid initial value
    config = TyConf(port=(int, 8080, range(1024, 65535)))
    assert config.port == 8080
    
    # Should fail with invalid initial value
    with pytest.raises(ValueError):
        config = TyConf(port=(int, 80, range(1024, 65535)))
```

---

## Error Handling

### Validate Early

Validate configuration at startup:

```python
from tyconf.validators import range, regex, one_of

def validate_config(config):
    """Validate configuration before starting app."""
    errors = []
    
    # Check required values
    if not config.database_url:
        errors.append("DATABASE_URL is required")
    
    # Check ranges (if not using validators)
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

**Better:** Use validators to enforce rules automatically:

```python
# Validators handle validation automatically
config = TyConf(
    port=(int, 8080, range(1024, 65535)),
    environment=(str, "dev", one_of("dev", "staging", "prod")),
    admin_email=(str, "admin@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$'))
)
# Validation errors are raised immediately on invalid assignment
```

### Handle Type Errors Gracefully

Provide helpful error messages when loading from environment:

```python
def load_int_from_env(key, default, validator=None):
    """Load integer from environment with error handling."""
    value = os.getenv(key)
    if value is None:
        return default
    
    try:
        int_value = int(value)
        # Apply validator if provided
        if validator and not validator(int_value):
            raise ValueError(f"Value {int_value} failed validation")
        return int_value
    except ValueError as e:
        raise ValueError(
            f"Environment variable {key}='{value}' is not a valid integer or failed validation: {e}"
        )

# Usage
from tyconf.validators import range

config = TyConf(
    port=(int, load_int_from_env('PORT', 8080, lambda x: 1024 <= x <= 65535)),
    workers=(int, load_int_from_env('WORKERS', 4, lambda x: 1 <= x <= 16))
)
```

### Handle Validation Errors

Catch and handle validation errors appropriately:

```python
from tyconf import TyConf
from tyconf.validators import range, regex

config = TyConf(
    port=(int, 8080, range(1024, 65535)),
    email=(str, "admin@example.com", regex(r'^[\w\.-]+@[\w\.-]+\.\w+$'))
)

# Handle validation errors
try:
    config.port = 80
except ValueError as e:
    print(f"Invalid port: {e}")
    config.port = 8080  # Use default

try:
    config.email = "invalid-email"
except ValueError as e:
    print(f"Invalid email: {e}")
    # Keep current value or use default

# Or validate before setting
def safe_set_port(config, port):
    """Safely set port with fallback."""
    try:
        config.port = port
    except ValueError:
        print(f"Port {port} is invalid, using default 8080")
        config.port = 8080

safe_set_port(config, 80)  # Will use default
```

### Custom Error Messages

Provide clear error messages in custom validators:

```python
def validate_api_key(value):
    """Validate API key format."""
    if not value:
        raise ValueError("API key cannot be empty")
    if not value.startswith('sk_'):
        raise ValueError("API key must start with 'sk_' prefix")
    if len(value) != 32:
        raise ValueError(f"API key must be 32 characters, got {len(value)}")
    if not all(c in 'abcdef0123456789_' for c in value.lower()):
        raise ValueError("API key contains invalid characters")
    return True

config = TyConf(
    api_key=(str, "sk_" + "a" * 29, validate_api_key)
)

# Clear error messages help users fix issues
try:
    config.api_key = "invalid"
except ValueError as e:
    print(f"Configuration error: {e}")
    # Output: Configuration error: API key must start with 'sk_' prefix
```

### Validation in Production

Best practices for production:

```python
from tyconf import TyConf
from tyconf.validators import range, one_of, regex

def create_production_config():
    """Create validated production config."""
    try:
        config = TyConf(
            # All values are validated on creation
            ENVIRONMENT=(str, "production", True),
            host=(str, os.getenv('HOST', '0.0.0.0')),
            port=(int, int(os.getenv('PORT', '8080')), range(1024, 65535)),
            workers=(int, int(os.getenv('WORKERS', '4')), range(1, 16)),
            log_level=(str, os.getenv('LOG_LEVEL', 'INFO'), 
                      one_of("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
            admin_email=(str, os.getenv('ADMIN_EMAIL', 'admin@example.com'),
                        regex(r'^[\w\.-]+@[\w\.-]+\.\w+$'))
        )
        
        # Additional validation
        if config.ENVIRONMENT == "production" and config.debug:
            raise ValueError("Debug mode cannot be enabled in production")
        
        config.freeze()
        return config
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your environment variables and try again")
        sys.exit(1)

# Usage
config = create_production_config()
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
from tyconf.validators import range, one_of

def create_dev_config():
    """Create development configuration."""
    return TyConf(
        ENVIRONMENT=(str, "development", True),
        debug=(bool, True),
        log_level=(str, "DEBUG", one_of("DEBUG", "INFO", "WARNING", "ERROR")),
        workers=(int, 1, range(1, 4))
    )

def create_prod_config():
    """Create production configuration."""
    return TyConf(
        ENVIRONMENT=(str, "production", True),
        debug=(bool, False),
        log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR")),
        workers=(int, 4, range(1, 16))
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
from tyconf.validators import range, regex

def build_config():
    """Build configuration from multiple sources."""
    # Start with defaults (with validation)
    config = TyConf(
        host=(str, "localhost"),
        port=(int, 8080, range(1024, 65535)),
        debug=(bool, False)
    )
    
    # Load from file
    if os.path.exists('config.json'):
        settings = load_json('config.json')
        config.update(**settings)  # Validation happens here
    
    # Override from environment (validation happens automatically)
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
- ✅ Use validators to enforce value constraints
- ✅ Freeze production configs
- ✅ Validate configuration at startup
- ✅ Use descriptive names
- ✅ Use Optional for nullable values
- ✅ Provide clear error messages in custom validators
- ✅ Combine validators with all_of() and any_of() when needed

**Don't:**
- ❌ Use generic Any type
- ❌ Modify frozen configs
- ❌ Use mutable defaults (lists, dicts) across instances
- ❌ Skip validation
- ❌ Freeze during initialization
- ❌ Use both readonly and validator on the same property
- ❌ Put complex logic in lambda validators
- ❌ Over-validate (be reasonable with constraints)

Following these practices will help you build robust, maintainable applications with TyConf!
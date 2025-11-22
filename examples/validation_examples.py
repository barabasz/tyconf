"""Examples demonstrating TyConf validators."""

from tyconf import TyConf
from tyconf.validators import range, length, regex, one_of, all_of, any_of, not_in


def basic_validators_example():
    """Basic validator usage examples."""
    print("=" * 60)
    print("BASIC VALIDATORS")
    print("=" * 60)


    # Lambda validators - simple and quick
    config = TyConf(
        percentage=(int, 50, lambda x: 0 <= x <= 100),
        even_number=(int, 10, lambda x: x % 2 == 0),
    )

    print("\n1. Lambda Validators:")
    print(f"   Percentage: {config.percentage}")
    config.percentage = 75
    print(f"   Updated to: {config.percentage}")

    try:
        config.percentage = 150
    except ValueError as e:
        print(f"   ❌ Error: {e}")


    # Contains validator
    url_config = TyConf(
        api_url=(str, "https://api.example.com", contains("https://")),
        log_path=(str, "/var/log/app.log", contains("/log"))
    )

    print("\n4. Contains Validator:")
    print(f"   API URL: {url_config.api_url}")
    url_config.api_url = "https://secure.api.com"
    print(f"   Updated to: {url_config.api_url}")

    try:
        url_config.api_url = "http://insecure.com"
    except ValueError as e:
        print(f"   ❌ Error: Property 'api_url': {e}")

    print(f"\n   Log path: {url_config.log_path}")
    url_config.log_path = "/var/log/application.log"
    print(f"   Updated to: {url_config.log_path}")

    try:
        url_config.log_path = "/tmp/app.log"
    except ValueError as e:
        print(f"   ❌ Error: Property 'log_path': {e}")


    # Range validator
    port_config = TyConf(port=(int, 8080, range(1024, 65535)))

    print("\n2. Range Validator:")
    print(f"   Port: {port_config.port}")
    port_config.port = 3000
    print(f"   Updated to: {port_config.port}")

    try:
        port_config.port = 80
    except ValueError as e:
        print(f"   ❌ Error: Property 'port': {e}")


    # Length validator
    user_config = TyConf(username=(str, "admin", length(min_len=3, max_len=20)))

    print("\n3. Length Validator:")
    print(f"   Username: {user_config.username}")
    user_config.username = "john_doe"
    print(f"   Updated to: {user_config.username}")

    try:
        user_config.username = "ab"
    except ValueError as e:
        print(f"   ❌ Error: Property 'username': {e}")


def regex_validator_example():
    """Regex validator examples."""
    print("\n" + "=" * 60)
    print("REGEX VALIDATORS")
    print("=" * 60)

    config = TyConf(
        email=(str, "user@example.com", regex(r"^[\w\.-]+@[\w\.-]+\.\w+$")),
        phone=(str, "+48123456789", regex(r"^\+?[0-9]{9,15}$")),
    )

    print("\n1. Email Validation:")
    print(f"   Email: {config.email}")
    config.email = "john.doe@company.com"
    print(f"   Updated to: {config.email}")

    try:
        config.email = "invalid-email"
    except ValueError as e:
        print(f"   ❌ Error: Property 'email': {e}")

    print("\n2. Phone Validation:")
    print(f"   Phone: {config.phone}")
    config.phone = "123456789"
    print(f"   Updated to: {config.phone}")

    try:
        config.phone = "12345"
    except ValueError as e:
        print(f"   ❌ Error: Property 'phone': {e}")


def choice_validator_example():
    """Choice validator examples."""
    print("\n" + "=" * 60)
    print("CHOICE VALIDATORS")
    print("=" * 60)

    config = TyConf(
        log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR")),
        environment=(str, "dev", one_of("dev", "staging", "prod")),
    )

    print("\n1. Log Level (one_of):")
    print(f"   Log level: {config.log_level}")
    config.log_level = "DEBUG"
    print(f"   Updated to: {config.log_level}")

    try:
        config.log_level = "TRACE"
    except ValueError as e:
        print(f"   ❌ Error: Property 'log_level': {e}")

    print("\n2. Environment:")
    print(f"   Environment: {config.environment}")
    config.environment = "prod"
    print(f"   Updated to: {config.environment}")


def combined_validators_example():
    """Examples of combining multiple validators."""
    print("\n" + "=" * 60)
    print("COMBINED VALIDATORS")
    print("=" * 60)

    # all_of - all validators must pass
    config = TyConf(
        username=(
            str,
            "admin",
            all_of(length(min_len=3, max_len=20), regex(r"^[a-zA-Z0-9_]+$")),
        ),
        port=(int, 8080, all_of(range(1024, 65535), not_in(3000, 5000, 8000))),
    )

    print("\n1. Username (length + pattern):")
    print(f"   Username: {config.username}")
    config.username = "john_doe"
    print(f"   Updated to: {config.username}")

    try:
        config.username = "ab"
    except ValueError as e:
        print(f"   ❌ Error (too short): Property 'username': {e}")

    try:
        config.username = "john@doe"
    except ValueError as e:
        print(f"   ❌ Error (invalid chars): Property 'username': {e}")

    print("\n2. Port (range + not reserved):")
    print(f"   Port: {config.port}")
    config.port = 9000
    print(f"   Updated to: {config.port}")

    try:
        config.port = 3000
    except ValueError as e:
        print(f"   ❌ Error (reserved): Property 'port': {e}")


def any_of_validator_example():
    """Examples of any_of validator."""
    print("\n" + "=" * 60)
    print("ANY_OF VALIDATORS (Alternative Validation)")
    print("=" * 60)

    # Accept either email OR phone format
    config = TyConf(
        contact=(
            str,
            "user@example.com",
            any_of(
                regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"),  # Email
                regex(r"^\+?[0-9]{9,15}$"),  # Phone
            ),
        )
    )

    print("\n1. Contact (email OR phone):")
    print(f"   Contact: {config.contact}")

    # Valid email
    config.contact = "john@company.com"
    print(f"   ✓ Email: {config.contact}")

    # Valid phone
    config.contact = "+48123456789"
    print(f"   ✓ Phone: {config.contact}")

    # Invalid - neither email nor phone
    try:
        config.contact = "invalid"
    except ValueError as e:
        print(f"   ❌ Error: Property 'contact': {e}")


def custom_validator_example():
    """Examples of custom validator functions."""
    print("\n" + "=" * 60)
    print("CUSTOM VALIDATORS")
    print("=" * 60)

    def validate_password(value):
        """Validate password strength."""
        errors = []
        if len(value) < 8:
            errors.append("at least 8 characters")
        if not any(c.isupper() for c in value):
            errors.append("uppercase letter")
        if not any(c.isdigit() for c in value):
            errors.append("digit")

        if errors:
            raise ValueError(f"must contain: {', '.join(errors)}")
        return True

    def validate_port_range(value):
        """Validate port is in valid range and even."""
        if not (1024 <= value <= 65535):
            raise ValueError("port must be between 1024 and 65535")
        if value % 2 != 0:
            raise ValueError("port must be even number")
        return True

    config = TyConf(
        password=(str, "Secret123", validate_password),
        port=(int, 8080, validate_port_range),
    )

    print("\n1. Password Strength Validator:")
    print(f"   Password: {'*' * len(config.password)}")

    try:
        config.password = "short"
    except ValueError as e:
        print(f"   ❌ Error: Property 'password': {e}")

    config.password = "NewPassword123"
    print("   ✓ Password updated")

    print("\n2. Custom Port Validator:")
    print(f"   Port: {config.port}")

    try:
        config.port = 8081  # Odd number
    except ValueError as e:
        print(f"   ❌ Error: Property 'port': {e}")

    config.port = 9000  # Even and in range
    print(f"   ✓ Port updated to: {config.port}")


def real_world_example():
    """Real-world application configuration with validators."""
    print("\n" + "=" * 60)
    print("REAL-WORLD APPLICATION CONFIGURATION")
    print("=" * 60)

    import os

    config = TyConf(
        # Application metadata (readonly, no validators needed)
        APP_NAME=(str, "WebAPI", True),
        VERSION=(str, "1.0.0", True),
        # Server settings with validation
        host=(str, "localhost", regex(r"^[\w\.-]+$")),
        port=(int, 8080, range(1024, 65535)),
        workers=(int, 4, range(1, 16)),
        # Database with validation
        db_pool_size=(int, 10, range(1, 100)),
        db_timeout=(int, 30, range(5, 300)),
        # API settings
        rate_limit=(int, 100, range(10, 10000)),
        max_upload_mb=(int, 10, range(1, 100)),
        # Security
        api_key=(
            str,
            "dev-key-12345",
            all_of(length(min_len=10, max_len=100), regex(r"^[a-zA-Z0-9\-_]+$")),
        ),
        # Environment
        environment=(str, "dev", one_of("dev", "staging", "prod")),
        log_level=(str, "INFO", one_of("DEBUG", "INFO", "WARNING", "ERROR")),
    )

    print(f"\n{config.APP_NAME} v{config.VERSION}")
    print(f"Environment: {config.environment}")
    print("-" * 60)

    # Display configuration
    config.show()

    # Simulate environment overrides with validation
    print("\n" + "=" * 60)
    print("APPLYING ENVIRONMENT OVERRIDES")
    print("=" * 60)

    # Valid override
    if os.getenv("PORT"):
        try:
            new_port = int(os.getenv("PORT"))
            config.port = new_port
            print(f"✓ Port updated to: {new_port}")
        except ValueError as e:
            print(f"❌ Invalid PORT: {e}")

    # Simulate invalid environment variable
    print("\nSimulating invalid environment values:")
    try:
        config.workers = 20  # Too many
    except ValueError as e:
        print(f"❌ WORKERS error: {e}")

    try:
        config.environment = "test"  # Invalid
    except ValueError as e:
        print(f"❌ ENVIRONMENT error: {e}")

    print("\n✓ Configuration validated and ready!")


def validation_vs_readonly_example():
    """Show difference between validators and readonly."""
    print("\n" + "=" * 60)
    print("VALIDATORS vs READ-ONLY")
    print("=" * 60)

    config = TyConf(
        # Read-only - value never changes
        VERSION=(str, "1.0.0", True),
        # Validator - value can change but must be valid
        port=(int, 8080, range(1024, 65535)),
    )

    print("\n1. Read-only property:")
    print(f"   VERSION: {config.VERSION}")
    try:
        config.VERSION = "2.0.0"
    except AttributeError as e:
        print(f"   ❌ Cannot modify: {e}")

    print("\n2. Property with validator:")
    print(f"   Port: {config.port}")
    config.port = 3000
    print(f"   ✓ Updated to: {config.port}")

    try:
        config.port = 80
    except ValueError as e:
        print(f"   ❌ Invalid value: Property 'port': {e}")

    print("\n   Key difference:")
    print("   - Read-only: Value NEVER changes after creation")
    print("   - Validator: Value CAN change but must pass validation")


if __name__ == "__main__":
    """Run all validation examples."""

    print("\n" + "=" * 60)
    print("TyConf Validators - Complete Examples")
    print("=" * 60)

    basic_validators_example()
    regex_validator_example()
    choice_validator_example()
    combined_validators_example()
    any_of_validator_example()
    custom_validator_example()
    real_world_example()
    validation_vs_readonly_example()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)

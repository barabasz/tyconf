"""Real-world web application configuration example."""

import os

from tyconf import TyConf

# Application configuration
app_config = TyConf(
    # Application metadata (read-only)
    APP_NAME=(str, "WebAPI", True),
    VERSION=(str, "2.0.0", True),
    ENVIRONMENT=(str, os.getenv("ENV", "development"), True),
    MAX_UPLOAD_SIZE=(int, 10 * 1024 * 1024, True),  # 10MB
    # Server settings (mutable)
    host=(str, "localhost"),
    port=(int, 5000),
    debug=(bool, True),
    workers=(int, 4),
    # Database (mutable) - ✅ Modern syntax
    database_url=(str | None, None),
    db_pool_size=(int, 10),
    db_timeout=(int, 30),
    # Features (mutable) - ✅ Modern syntax
    enable_api=(bool, True),
    enable_websocket=(bool, False),
    rate_limit=(int | None, 100),
    allowed_origins=(list, ["http://localhost:3000"]),
)

# Configure from environment variables
app_config.debug = os.getenv("DEBUG", "false").lower() == "true"
app_config.port = int(os.getenv("PORT", "5000"))
app_config.database_url = os.getenv("DATABASE_URL")

# Explicit variable assignment to satisfy MyPy strict checks
workers_env = os.getenv("WORKERS")
if workers_env:
    app_config.workers = int(workers_env)

# Display current configuration
print(f"Starting {app_config.APP_NAME} v{app_config.VERSION}")
print(f"Environment: {app_config.ENVIRONMENT}")
app_config.show()

# Freeze configuration before starting app
# This prevents accidental modifications during runtime
app_config.freeze()
print(f"\nConfiguration locked: {app_config.frozen}")


# Start application (pseudo-code)
def start_application(config: TyConf) -> None:
    """Start the application with given config."""
    print(f"\n🚀 Server starting on {config.host}:{config.port}")
    print(f"   Debug mode: {config.debug}")
    print(f"   Workers: {config.workers}")

    if config.database_url:
        print("   Database: Connected")
    else:
        print("   Database: Not configured")

    if config.enable_api:
        print(f"   API: Enabled (rate limit: {config.rate_limit} req/min)")

    if config.enable_websocket:
        print("   WebSocket: Enabled")

    print(f"\n✅ {config.APP_NAME} is ready!")


# Start the app
start_application(app_config)

# Try to modify frozen config (will fail)
try:
    app_config.port = 8080
except AttributeError as e:
    print(f"\n❌ Cannot modify config: {e}")

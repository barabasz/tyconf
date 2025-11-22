"""Examples demonstrating TyConf serialization features."""

import json
import os

from tyconf import TyConf
from tyconf.validators import range


def json_serialization_example() -> None:
    """Demonstrate JSON serialization."""
    print("=" * 60)
    print("JSON SERIALIZATION")
    print("=" * 60)

    # Create configuration
    config = TyConf(
        host=(str, "localhost"),
        port=(int, 8080, range(1024, 65535)),
        debug=(bool, True),
        VERSION=(str, "1.0.0", True),
    )

    print("\n1. Export to JSON (values only):")
    json_str = config.to_json(values_only=True)
    print(json_str)

    print("\n2. Export to JSON (full metadata):")
    json_str = config.to_json()

    # Fix: Check for None before slicing because to_json returns str | None
    if json_str is not None:
        print(json_str[:200] + "...")

    print("\n3. Save to file:")
    config.to_json("config.json")
    print("✓ Saved to config.json")

    print("\n4. Load from file:")
    loaded = TyConf.from_json("config.json")
    print(f"   Loaded: host={loaded.host}, port={loaded.port}")

    # Cleanup
    os.remove("config.json")


def toml_serialization_example() -> None:
    """Demonstrate TOML serialization."""
    print("\n" + "=" * 60)
    print("TOML SERIALIZATION")
    print("=" * 60)

    config = TyConf(database=(str, "app.db"), timeout=(int, 30), retry=(bool, True))

    print("\n1. Export to TOML (values only):")
    try:
        toml_str = config.to_toml(values_only=True)

        # Fix: Handle optional return type explicitly
        if toml_str is not None:
            print(toml_str)

        print("\n2. Save to file:")
        config.to_toml("config.toml")
        print("✓ Saved to config.toml")

        # Cleanup
        os.remove("config.toml")
    except ImportError:
        print("⚠️  TOML write requires: pip install tyconf[toml]")

    print("\n3. Load from TOML string:")
    toml_data = """
database = "production.db"
timeout = 60
retry = false
"""
    schema = {"database": (str, "app.db"), "timeout": (int, 30), "retry": (bool, True)}
    loaded = TyConf.from_toml(toml_data, schema=schema)
    print(f"   Loaded: database={loaded.database}, timeout={loaded.timeout}")


def environment_variables_example() -> None:
    """Demonstrate environment variable loading."""
    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLES")
    print("=" * 60)

    # Set environment variables
    os.environ["APP_HOST"] = "0.0.0.0"
    os.environ["APP_PORT"] = "3000"
    os.environ["APP_DEBUG"] = "true"

    print("\n1. Load from environment:")
    print("   Environment: APP_HOST=0.0.0.0, APP_PORT=3000, APP_DEBUG=true")

    config = TyConf.from_env(
        "APP_", schema={"host": (str, "localhost"), "port": (int, 8080), "debug": (bool, False)}
    )

    print(f"   Loaded: host={config.host}, port={config.port}, debug={config.debug}")

    print("\n2. Merge into existing config:")
    config2 = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, False))
    print(f"   Before: host={config2.host}, port={config2.port}")

    config2.load_env("APP_")
    print(f"   After:  host={config2.host}, port={config2.port}")

    # Cleanup
    del os.environ["APP_HOST"]
    del os.environ["APP_PORT"]
    del os.environ["APP_DEBUG"]


def mixed_sources_example() -> None:
    """Demonstrate loading from multiple sources."""
    print("\n" + "=" * 60)
    print("MIXED SOURCES (Real-world pattern)")
    print("=" * 60)

    # 1. Start with defaults
    config = TyConf(
        host=(str, "localhost"), port=(int, 8080), debug=(bool, False), workers=(int, 4)
    )
    print("\n1. Defaults:")
    config.show()

    # 2. Load from JSON file
    json_config = {"host": "0.0.0.0", "workers": 8}
    with open("overrides.json", "w") as f:
        json.dump(json_config, f)

    config.load_json("overrides.json")
    print("\n2. After loading JSON (host, workers changed):")
    config.show()

    # 3. Override from environment
    os.environ["APP_PORT"] = "3000"
    os.environ["APP_DEBUG"] = "true"

    config.load_env("APP_")
    print("\n3. After loading ENV (port, debug changed):")
    config.show()

    # 4. Freeze for production
    config.freeze()
    print("\n4. Configuration frozen for production ✓")

    # Cleanup
    os.remove("overrides.json")
    del os.environ["APP_PORT"]
    del os.environ["APP_DEBUG"]


def schema_vs_metadata_example() -> None:
    """Explain schema vs metadata formats."""
    print("\n" + "=" * 60)
    print("SCHEMA vs METADATA")
    print("=" * 60)

    config = TyConf(host=(str, "localhost"), port=(int, 8080))

    print("\n1. Values-only format (requires schema):")
    values_dict = config.to_dict(values_only=True)
    print(f"   Data: {values_dict}")
    print("   ⚠️  Needs schema when loading:")
    print("   schema = {'host': (str, ''), 'port': (int, 0)}")

    print("\n2. Full metadata format (self-describing):")
    full_dict = config.to_dict(values_only=False)
    print(f"   Data: {json.dumps(full_dict, indent=2)}")
    print("   ✓ Contains types, defaults, readonly flags")
    print("   ✓ No schema needed when loading")


if __name__ == "__main__":
    """Run all serialization examples."""

    print("\n" + "=" * 60)
    print("TyConf Serialization - Complete Examples")
    print("=" * 60)

    json_serialization_example()
    toml_serialization_example()
    environment_variables_example()
    mixed_sources_example()
    schema_vs_metadata_example()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)

"""Basic TyConf usage examples."""

from tyconf import TyConf

# Create configuration
config = TyConf(host=(str, "localhost"), port=(int, 8080), debug=(bool, True))

# Read values - two ways
print(f"Host: {config.host}")  # Attribute access
print(f"Port: {config['port']}")  # Dict-style access

# Modify values - two ways
config.debug = False  # Attribute style
config["port"] = 3000  # Dict style

# Display all properties
config.show()
# Output:
# Configuration properties:
# --------------------------------------------
# debug            = False           bool
# host             = 'localhost'     str
# port             = 3000            int
# --------------------------------------------

# Check if property exists
if "debug" in config:
    print(f"Debug mode: {config.debug}")

# Iterate over properties
for key, value in config.items():
    print(f"{key} = {value}")
    
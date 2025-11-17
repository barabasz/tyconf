"""Advanced TyConf features."""

from tyconf import TyConf
from typing import Optional, Union

# Optional and Union types
config = TyConf(api_key=(Optional[str], None), port=(Union[int, str], 8080), timeout=(int, 30))

# Optional can be None or string
config.api_key = "secret123"
config.api_key = None  # Both valid

# Union accepts multiple types
config.port = 9000  # int - OK
config.port = "auto"  # str - OK

# Read-only properties
app = TyConf(VERSION=(str, "1.0.0", True), debug=(bool, True))  # Read-only  # Mutable

print(app.VERSION)  # Can read
# app.VERSION = "2.0"  # Error! Read-only

# Freeze entire configuration
app.freeze()
print(f"Frozen: {app.frozen}")  # True

# app.debug = False  # Error! Config is frozen

app.unfreeze()
app.debug = False  # OK now

# Copy configuration
backup = app.copy()
backup.debug = True  # Doesn't affect original

# Reset to defaults
config = TyConf(debug=(bool, False), port=(int, 8080))

config.debug = True
config.port = 3000

config.reset()  # Back to defaults
print(config.debug)  # False
print(config.port)  # 8080
"""
TyConf - Type-safe Configuration Management

TyConf (Typed Config) is a modern Python library for managing application
configuration with runtime type validation and an intuitive API.
"""

from . import validators
from .core import PropertyDescriptor, TyConf

__all__ = ["TyConf", "PropertyDescriptor", "validators"]
__version__ = "1.2.1"
__date__ = "2025-01-22"
__author__ = "barabasz"
__license__ = "MIT"
__copyright__ = "2025, barabasz"
__url__ = "https://github.com/barabasz/tyconf"

"""
Centralized model imports
"""

from app.database.connection import BaseModel
from .account import Account
from .property import Property
from .address import Address
from .visit import Visit
from .proposal import Proposal

# List of all models (useful for migrations and other scripts)
__all__ = ["BaseModel", "Account", "Property", "Address", "Visit", "Proposal"]

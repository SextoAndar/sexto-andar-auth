"""
Centralized model imports
"""

from app.database.connection import BaseModel
from .account import Account

# List of models (auth-only)
__all__ = ["BaseModel", "Account"]

"""
API v1 routers
"""

# Importar todos los routers
from .chatbot import router as chatbot
from .distributors import router as distributors
from .conversations import router as conversations
from .leads import router as leads
from .admin import router as admin
from .stats import router as stats
from .inventory import router as inventory  # NUEVO

__all__ = [
    "chatbot",
    "distributors",
    "conversations", 
    "leads",
    "admin",
    "stats",
    "inventory"  # NUEVO
]
# app/routes/__init__.py
"""
API routes package.
"""

from .upload import router as upload_router
from .stats import router as stats_router

__all__ = ["upload_router", "stats_router"]
"""
Webhooks module for handling external service webhooks.
"""

from .lemonsqueezy import router as lemonsqueezy_router

__all__ = ["lemonsqueezy_router"]

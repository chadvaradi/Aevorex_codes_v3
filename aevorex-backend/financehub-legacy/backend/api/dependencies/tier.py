"""
Tier/Subscription dependency for FastAPI endpoints.
"""

from fastapi import Request, HTTPException, status
from backend.config import settings


async def get_current_tier(request: Request) -> str:
    """
    FastAPI dependency to get the current user's subscription tier.
    
    For now, this returns a default tier based on configuration.
    In the future, this should be integrated with the subscription service
    to return the actual user's tier based on their subscription status.
    
    Returns:
        str: The user's subscription tier ("free", "pro", "team", "enterprise")
    """
    # TODO: Integrate with subscription service to get actual user tier
    # For now, return a default tier based on environment or configuration
    
    # Check if subscription system is enabled
    if not settings.SUBSCRIPTION.SUBSCRIPTION_ENABLED:
        # If subscription is disabled, allow all features (development mode)
        return "enterprise"
    
    # For MVP, we'll return "pro" as default to allow access to search endpoints
    # This should be replaced with actual user authentication and subscription checking
    return "pro"



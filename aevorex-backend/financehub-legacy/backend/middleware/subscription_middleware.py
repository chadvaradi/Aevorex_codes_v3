"""
Subscription Middleware for FinanceHub
=====================================

Middleware that checks for active subscriptions on protected endpoints.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status, Depends

from ..models.subscription import (
    SubscriptionPlan,
    UserWithSubscription,
    SubscriptionCheckResponse,
)
from .jwt_auth.deps import get_current_user
from ..core.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class SubscriptionMiddleware:
    """Middleware for subscription-based access control."""

    def __init__(self, subscription_service: Optional[SubscriptionService] = None):
        self.subscription_service = subscription_service

    async def get_user_subscription(
        self, user_id: str
    ) -> Optional[UserWithSubscription]:
        """Get user with subscription information."""
        if not self.subscription_service:
            from ..core.services.subscription_service import get_subscription_service

            self.subscription_service = await get_subscription_service()
        return await self.subscription_service.get_user_with_subscription(user_id)

    def require_active_subscription(
        self, min_plan: SubscriptionPlan = SubscriptionPlan.FREE
    ):
        """Dependency that requires active subscription."""

        async def _require_active_subscription(
            request: Request, current_user: dict = Depends(get_current_user)
        ) -> UserWithSubscription:
            try:
                user_id = current_user.get("user_id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User ID not found in token",
                    )

                # Get user subscription
                user_with_sub = await self.get_user_subscription(user_id)
                if not user_with_sub:
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail="No subscription found",
                    )

                # Check if subscription is active
                if not user_with_sub.has_active_subscription:
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail="No active subscription",
                    )

                # Check plan level
                if not self._check_plan_access(user_with_sub.plan, min_plan):
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail=f"Plan {user_with_sub.plan} does not have access to this feature. Required: {min_plan}",
                    )

                return user_with_sub
            except HTTPException:
                raise
            except Exception as e:
                print(f"[ERROR] Subscription middleware error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Subscription check failed: {str(e)}",
                )

        return _require_active_subscription

    def require_plan(self, required_plan: SubscriptionPlan):
        """Dependency that requires specific plan level."""

        async def _require_plan(
            request: Request, current_user: dict = Depends(get_current_user)
        ) -> UserWithSubscription:
            user_id = current_user.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID not found in token",
                )

            # Get user subscription
            user_with_sub = await self.get_user_subscription(user_id)
            if not user_with_sub:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="No subscription found",
                )

            # Check plan level
            if not self._check_plan_access(user_with_sub.plan, required_plan):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Plan {user_with_sub.plan} does not have access to this feature. Required: {required_plan}",
                )

            return user_with_sub

        return _require_plan

    def _check_plan_access(
        self, user_plan: SubscriptionPlan, required_plan: SubscriptionPlan
    ) -> bool:
        """Check if user plan has access to required plan level."""
        plan_hierarchy = {
            SubscriptionPlan.FREE: 0,
            SubscriptionPlan.PRO: 1,
            SubscriptionPlan.TEAM: 2,
            SubscriptionPlan.ENTERPRISE: 3,
        }

        user_level = plan_hierarchy.get(user_plan, 0)
        required_level = plan_hierarchy.get(required_plan, 0)

        return user_level >= required_level

    async def check_subscription_status(
        self, user_id: str
    ) -> SubscriptionCheckResponse:
        """Check subscription status for a user."""
        user_with_sub = await self.get_user_subscription(user_id)

        if not user_with_sub:
            return SubscriptionCheckResponse(
                user_id=user_id,
                has_active_subscription=False,
                plan=SubscriptionPlan.FREE,
                status=None,
            )

        return SubscriptionCheckResponse(
            user_id=user_id,
            has_active_subscription=user_with_sub.has_active_subscription,
            plan=user_with_sub.plan,
            status=user_with_sub.subscription.status
            if user_with_sub.subscription
            else None,
            current_period_end=user_with_sub.subscription.current_period_end
            if user_with_sub.subscription
            else None,
            trial_end=user_with_sub.subscription.trial_end
            if user_with_sub.subscription
            else None,
        )


# Global middleware instance - will be initialized lazily
subscription_middleware = None


def get_subscription_middleware() -> SubscriptionMiddleware:
    """Get subscription middleware instance."""
    global subscription_middleware
    if subscription_middleware is None:
        # Create middleware with lazy service initialization
        subscription_middleware = SubscriptionMiddleware()
    return subscription_middleware


# Convenience dependencies
def require_pro_plan():
    """Require Pro plan or higher."""

    async def _require_pro_plan(
        request: Request, current_user: dict = Depends(get_current_user)
    ) -> UserWithSubscription:
        middleware = get_subscription_middleware()
        dependency_func = middleware.require_plan(SubscriptionPlan.PRO)
        return await dependency_func(request, current_user)

    return _require_pro_plan


def require_team_plan():
    """Require Team plan or higher."""

    async def _require_team_plan(
        request: Request, current_user: dict = Depends(get_current_user)
    ) -> UserWithSubscription:
        middleware = get_subscription_middleware()
        dependency_func = middleware.require_plan(SubscriptionPlan.TEAM)
        return await dependency_func(request, current_user)

    return _require_team_plan


def require_enterprise_plan():
    """Require Enterprise plan."""

    async def _require_enterprise_plan(
        request: Request, current_user: dict = Depends(get_current_user)
    ) -> UserWithSubscription:
        middleware = get_subscription_middleware()
        dependency_func = middleware.require_plan(SubscriptionPlan.ENTERPRISE)
        return await dependency_func(request, current_user)

    return _require_enterprise_plan


def require_active_subscription():
    """Require any active subscription."""

    async def _require_active_subscription(
        request: Request, current_user: dict = Depends(get_current_user)
    ) -> UserWithSubscription:
        middleware = get_subscription_middleware()
        dependency_func = middleware.require_active_subscription()
        return await dependency_func(request, current_user)

    return _require_active_subscription

"""
Subscription Models for FinanceHub
=================================

Pydantic models for user subscriptions and billing management.
"""

from datetime import datetime
from typing import Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
import uuid


class SubscriptionStatus(str, Enum):
    """Valid subscription statuses."""

    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    CANCELLED = "cancelled"  # Alternative spelling
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"
    INACTIVE = "inactive"


class SubscriptionPlan(str, Enum):
    """Available subscription plans."""

    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class PaymentProvider(str, Enum):
    """Supported payment providers."""

    STRIPE = "stripe"
    LEMON_SQUEEZY = "lemonsqueezy"
    PADDLE = "paddle"


class User(BaseModel):
    """User model for subscription management."""

    id: Union[str, uuid.UUID] = Field(..., description="Unique user ID")
    email: str = Field(..., description="User email address")
    auth_provider_id: Optional[str] = Field(
        None, description="External auth provider ID"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether user account is active")

    model_config = ConfigDict(from_attributes=True)


class Subscription(BaseModel):
    """Subscription model for billing management."""

    id: Union[str, uuid.UUID] = Field(..., description="Unique subscription ID")
    user_id: Union[str, uuid.UUID] = Field(..., description="Associated user ID")
    external_id: str = Field(..., description="External provider subscription ID")
    provider: PaymentProvider = Field(..., description="Payment provider")
    plan: SubscriptionPlan = Field(..., description="Subscription plan")
    status: SubscriptionStatus = Field(..., description="Current subscription status")
    current_period_start: datetime = Field(
        ..., description="Current billing period start"
    )
    current_period_end: datetime = Field(..., description="Current billing period end")
    trial_start: Optional[datetime] = Field(None, description="Trial period start")
    trial_end: Optional[datetime] = Field(None, description="Trial period end")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    """Model for creating new subscriptions."""

    user_id: Union[str, uuid.UUID]
    external_id: str
    provider: PaymentProvider
    plan: SubscriptionPlan
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None


class SubscriptionUpdate(BaseModel):
    """Model for updating subscriptions."""

    status: Optional[SubscriptionStatus] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None


class UserWithSubscription(BaseModel):
    """User model with subscription information."""

    user: User
    subscription: Optional[Subscription] = None

    @property
    def has_active_subscription(self) -> bool:
        """Check if user has active subscription."""
        if not self.subscription:
            return False
        return self.subscription.status in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        ]

    @property
    def plan(self) -> SubscriptionPlan:
        """Get current plan."""
        if not self.subscription:
            return SubscriptionPlan.FREE
        return self.subscription.plan


class WebhookEvent(BaseModel):
    """Generic webhook event model."""

    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type")
    provider: PaymentProvider = Field(..., description="Payment provider")
    data: dict = Field(..., description="Event payload")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionCheckResponse(BaseModel):
    """Response model for subscription status checks."""

    user_id: str
    has_active_subscription: bool
    plan: SubscriptionPlan
    status: Optional[SubscriptionStatus] = None
    current_period_end: Optional[datetime] = None
    trial_end: Optional[datetime] = None

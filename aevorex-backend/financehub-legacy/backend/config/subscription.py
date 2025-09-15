"""
Subscription Configuration Settings
=================================

Configuration for payment providers and subscription management.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class StripeSettings(BaseSettings):
    """Stripe payment provider configuration."""

    # API Keys
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(
        default=None, description="Stripe publishable key"
    )
    STRIPE_SECRET_KEY: Optional[str] = Field(
        default=None, description="Stripe secret key"
    )
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(
        default=None, description="Stripe webhook endpoint secret"
    )

    # Product/Price IDs
    STRIPE_PRO_MONTHLY_PRICE_ID: Optional[str] = Field(
        default=None, description="Stripe Pro monthly price ID"
    )
    STRIPE_PRO_YEARLY_PRICE_ID: Optional[str] = Field(
        default=None, description="Stripe Pro yearly price ID"
    )
    STRIPE_TEAM_MONTHLY_PRICE_ID: Optional[str] = Field(
        default=None, description="Stripe Team monthly price ID"
    )
    STRIPE_TEAM_YEARLY_PRICE_ID: Optional[str] = Field(
        default=None, description="Stripe Team yearly price ID"
    )
    STRIPE_ENTERPRISE_MONTHLY_PRICE_ID: Optional[str] = Field(
        default=None, description="Stripe Enterprise monthly price ID"
    )
    STRIPE_ENTERPRISE_YEARLY_PRICE_ID: Optional[str] = Field(
        default=None, description="Stripe Enterprise yearly price ID"
    )

    # Feature flags
    STRIPE_ENABLED: bool = Field(default=False, description="Whether Stripe is enabled")

    class Config:
        env_prefix = "STRIPE_"


class LemonSqueezySettings(BaseSettings):
    """Lemon Squeezy payment provider configuration."""

    # API Keys
    LEMON_SQUEEZY_API_KEY: Optional[str] = Field(
        default=None, description="Lemon Squeezy API key"
    )
    LEMON_SQUEEZY_WEBHOOK_SECRET: Optional[str] = Field(
        default=None, description="Lemon Squeezy webhook secret"
    )

    # Store/Product IDs
    LEMON_SQUEEZY_STORE_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy store ID"
    )
    LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy Pro monthly variant ID"
    )
    LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy Pro yearly variant ID"
    )
    LEMON_SQUEEZY_TEAM_MONTHLY_VARIANT_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy Team monthly variant ID"
    )
    LEMON_SQUEEZY_TEAM_YEARLY_VARIANT_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy Team yearly variant ID"
    )
    LEMON_SQUEEZY_ENTERPRISE_MONTHLY_VARIANT_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy Enterprise monthly variant ID"
    )
    LEMON_SQUEEZY_ENTERPRISE_YEARLY_VARIANT_ID: Optional[str] = Field(
        default=None, description="Lemon Squeezy Enterprise yearly variant ID"
    )

    # Feature flags
    LEMON_SQUEEZY_ENABLED: bool = Field(
        default=False, description="Whether Lemon Squeezy is enabled"
    )

    @property
    def variant_to_plan_mapping(self) -> dict[str, str]:
        """Map Lemon Squeezy variant IDs to subscription plans."""
        return {
            self.LEMON_SQUEEZY_PRO_MONTHLY_VARIANT_ID: "pro",
            self.LEMON_SQUEEZY_PRO_YEARLY_VARIANT_ID: "pro",
            self.LEMON_SQUEEZY_TEAM_MONTHLY_VARIANT_ID: "team",
            self.LEMON_SQUEEZY_TEAM_YEARLY_VARIANT_ID: "team",
            self.LEMON_SQUEEZY_ENTERPRISE_MONTHLY_VARIANT_ID: "enterprise",
            self.LEMON_SQUEEZY_ENTERPRISE_YEARLY_VARIANT_ID: "enterprise",
        }

    class Config:
        env_prefix = "LEMON_SQUEEZY_"


class PaddleSettings(BaseSettings):
    """Paddle payment provider configuration."""

    # API Keys
    PADDLE_API_KEY: Optional[str] = Field(default=None, description="Paddle API key")
    PADDLE_WEBHOOK_SECRET: Optional[str] = Field(
        default=None, description="Paddle webhook secret"
    )

    # Product/Plan IDs
    PADDLE_PRO_MONTHLY_PLAN_ID: Optional[str] = Field(
        default=None, description="Paddle Pro monthly plan ID"
    )
    PADDLE_PRO_YEARLY_PLAN_ID: Optional[str] = Field(
        default=None, description="Paddle Pro yearly plan ID"
    )
    PADDLE_TEAM_MONTHLY_PLAN_ID: Optional[str] = Field(
        default=None, description="Paddle Team monthly plan ID"
    )
    PADDLE_TEAM_YEARLY_PLAN_ID: Optional[str] = Field(
        default=None, description="Paddle Team yearly plan ID"
    )
    PADDLE_ENTERPRISE_MONTHLY_PLAN_ID: Optional[str] = Field(
        default=None, description="Paddle Enterprise monthly plan ID"
    )
    PADDLE_ENTERPRISE_YEARLY_PLAN_ID: Optional[str] = Field(
        default=None, description="Paddle Enterprise yearly plan ID"
    )

    # Feature flags
    PADDLE_ENABLED: bool = Field(default=False, description="Whether Paddle is enabled")

    class Config:
        env_prefix = "PADDLE_"


class SubscriptionSettings(BaseSettings):
    """Main subscription configuration."""

    # Payment providers
    STRIPE: StripeSettings = Field(default_factory=StripeSettings)
    LEMON_SQUEEZY: LemonSqueezySettings = Field(default_factory=LemonSqueezySettings)
    PADDLE: PaddleSettings = Field(default_factory=PaddleSettings)

    # General settings
    DEFAULT_PROVIDER: str = Field(
        default="lemonsqueezy", description="Default payment provider"
    )

    # Trial settings
    TRIAL_DAYS: int = Field(
        default=14, description="Number of trial days for new subscriptions"
    )

    # Grace period settings
    GRACE_PERIOD_DAYS: int = Field(
        default=3, description="Grace period in days for past due subscriptions"
    )

    # Feature flags
    SUBSCRIPTION_ENABLED: bool = Field(
        default=True, description="Whether subscription system is enabled"
    )

    # Admin API key for metrics endpoint
    ADMIN_API_KEY: Optional[str] = Field(
        default=None, description="Admin API key for metrics access"
    )

    # Rate limiting configuration
    WEBHOOK_RATE_LIMIT: str = Field(
        default="60/minute", description="Rate limit for webhook endpoints"
    )
    API_RATE_LIMIT: str = Field(
        default="1000/minute", description="Rate limit for public API endpoints"
    )

    # Plan limits
    FREE_PLAN_DAILY_REQUESTS: int = Field(
        default=100, description="Daily request limit for free plan"
    )
    PRO_PLAN_DAILY_REQUESTS: int = Field(
        default=1000, description="Daily request limit for Pro plan"
    )
    TEAM_PLAN_DAILY_REQUESTS: int = Field(
        default=5000, description="Daily request limit for Team plan"
    )
    ENTERPRISE_PLAN_DAILY_REQUESTS: int = Field(
        default=50000, description="Daily request limit for Enterprise plan"
    )

    class Config:
        env_prefix = "SUBSCRIPTION_"

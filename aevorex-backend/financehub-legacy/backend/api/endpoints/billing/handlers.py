"""
Event-specific handlers for Lemon Squeezy webhooks
"""

import logging
from typing import Dict, Any
from datetime import datetime
from backend.core.services.subscription_service import SubscriptionService
from backend.models.subscription import (
    SubscriptionCreate,
    SubscriptionStatus,
    SubscriptionPlan,
    PaymentProvider,
)

logger = logging.getLogger(__name__)

STATUS_MAP = {
    "active": SubscriptionStatus.ACTIVE,
    "cancelled": SubscriptionStatus.CANCELLED,
    "on_trial": SubscriptionStatus.TRIALING,
    "past_due": SubscriptionStatus.PAST_DUE,
    "paused": SubscriptionStatus.INACTIVE,
}

PLAN_MAP = {
    "free": SubscriptionPlan.FREE,
    "pro": SubscriptionPlan.PRO,
    "team": SubscriptionPlan.TEAM,
    "enterprise": SubscriptionPlan.ENTERPRISE,
}


def parse_date(date_str):
    if date_str:
        try:
            return datetime.fromisoformat(date_str)
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
    return None


async def handle_subscription_created(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        # Try both user_id and customer_id (LemonSqueezy uses customer_id)
        user_id = attributes.get("user_id") or attributes.get("customer_id")
        if not user_id:
            logger.error(f"Missing user_id/customer_id in subscription created event: {data.get('id')}")
            return

        status_str = attributes.get("status", "").lower()
        status = STATUS_MAP.get(status_str, SubscriptionStatus.INACTIVE)
        
        # Try both variant_name and plan_name (LemonSqueezy uses plan_name)
        plan_str = (attributes.get("variant_name") or attributes.get("plan_name", "pro")).lower()
        plan = PLAN_MAP.get(plan_str, SubscriptionPlan.PRO)

        # Parse dates with fallbacks
        created_at = parse_date(attributes.get("created_at"))
        starts_at = parse_date(attributes.get("starts_at"))
        renews_at = parse_date(attributes.get("renews_at"))
        
        # If renews_at is None, use created_at + 30 days as fallback
        if renews_at is None and created_at:
            from datetime import timedelta
            renews_at = created_at + timedelta(days=30)
        elif renews_at is None:
            from datetime import datetime, timedelta
            renews_at = datetime.utcnow() + timedelta(days=30)
        
        subscription_data = SubscriptionCreate(
            user_id=user_id,
            external_id=str(data.get("id")),
            provider=PaymentProvider.LEMON_SQUEEZY,
            plan=plan,
            status=status,
            current_period_start=starts_at or created_at or datetime.utcnow(),
            current_period_end=renews_at,
            trial_start=parse_date(attributes.get("trial_starts_at")),
            trial_end=parse_date(attributes.get("trial_ends_at")),
        )
        await service.create_subscription(subscription_data)
        logger.info(f"Created subscription: {data.get('id')}")
    except Exception as e:
        logger.error(f"Error handling subscription created: {e}")


async def handle_subscription_updated(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        external_id = str(data.get("id"))
        status_str = attributes.get("status", "").lower()
        status = STATUS_MAP.get(status_str, SubscriptionStatus.INACTIVE)
        await service.update_subscription_status(external_id, status)
        logger.info(f"Updated subscription: {external_id}")
    except Exception as e:
        logger.error(f"Error handling subscription updated: {e}")


async def handle_subscription_cancelled(data: Dict[str, Any], service: SubscriptionService):
    try:
        external_id = str(data.get("id"))
        await service.update_subscription_status(external_id, SubscriptionStatus.CANCELLED)
        logger.info(f"Cancelled subscription: {external_id}")
    except Exception as e:
        logger.error(f"Error handling subscription cancelled: {e}")


async def handle_payment_success(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")
        amount = attributes.get("amount")
        currency = attributes.get("currency")
        invoice_id = attributes.get("invoice_id")
        if subscription_id:
            await service.record_payment_event(
                subscription_id=str(subscription_id),
                event_type="payment_success",
                amount=amount,
                currency=currency,
                invoice_id=invoice_id,
            )
            logger.info(f"Payment success for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")


async def handle_payment_failed(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")
        amount = attributes.get("amount")
        currency = attributes.get("currency")
        invoice_id = attributes.get("invoice_id")
        if subscription_id:
            await service.record_payment_event(
                subscription_id=str(subscription_id),
                event_type="payment_failed",
                amount=amount,
                currency=currency,
                invoice_id=invoice_id,
            )
            logger.info(f"Payment failed for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")


async def handle_plan_changed(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        external_id = str(data.get("id"))
        variant_id = attributes.get("variant_id")
        if variant_id is not None:
            # Map variant_id to plan string if possible
            # Assume variant_id maps directly to PLAN_MAP keys if string; else fallback
            plan_str = str(variant_id).lower()
        else:
            plan_str = attributes.get("variant_name", "pro").lower()
        new_plan = PLAN_MAP.get(plan_str, SubscriptionPlan.PRO)
        await service.update_subscription_plan(external_id, new_plan)
        logger.info(f"Plan changed for subscription: {external_id} → {new_plan}")
    except Exception as e:
        logger.error(f"Error handling plan changed: {e}")


async def dispatch_subscription_event(event_type: str, data: Dict[str, Any], service: SubscriptionService):
    if event_type == "subscription_created":
        await handle_subscription_created(data, service)
    elif event_type == "subscription_updated":
        await handle_subscription_updated(data, service)
    elif event_type == "subscription_cancelled":
        await handle_subscription_cancelled(data, service)
    elif event_type == "payment_success":
        await handle_payment_success(data, service)
    elif event_type == "payment_failed":
        await handle_payment_failed(data, service)
    elif event_type == "plan_changed":
        await handle_plan_changed(data, service)
    else:
        logger.warning(f"Unhandled subscription event type: {event_type}")
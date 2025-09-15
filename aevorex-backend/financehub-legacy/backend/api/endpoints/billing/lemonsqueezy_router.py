"""
Lemon Squeezy Webhook Router
============================

Handles webhook events from Lemon Squeezy for subscription management.
"""

import hashlib
import hmac
import logging
import os
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from backend.core.services.subscription_service import (
    get_subscription_service,
    SubscriptionService,
)
from backend.models.subscription import (
    SubscriptionCreate,
    SubscriptionStatus,
    PaymentProvider,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing/lemonsqueezy")


async def verify_webhook_signature(request: Request, webhook_secret: str) -> bool:
    """
    Verify the webhook signature from Lemon Squeezy.
    """
    try:
        signature = request.headers.get("x-signature")
        if not signature:
            logger.warning("No signature found in webhook headers")
            return False

        body = await request.body()

        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"), body, hashlib.sha256
        ).hexdigest()

        # Debug logging
        logger.info(f"Received signature: {signature}")
        logger.info(f"Expected signature: {expected_signature}")
        logger.info(f"Signatures match: {hmac.compare_digest(signature, expected_signature)}")

        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False


@router.post("")
async def handle_lemonsqueezy_webhook(
    request: Request,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Handle Lemon Squeezy webhook events.
    """
    webhook_secret = os.getenv("LEMON_SQUEEZY_WEBHOOK_SECRET")
    
    # Debug logging
    logger.info(f"Webhook secret loaded: {webhook_secret[:10]}..." if webhook_secret else "Webhook secret: None")

    if not webhook_secret:
        logger.error("LEMON_SQUEEZY_WEBHOOK_SECRET not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured",
        )

    if not await verify_webhook_signature(request, webhook_secret):
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature"
        )

    try:
        payload = await request.json()
        event_name = payload.get("meta", {}).get("event_name")
        data = payload.get("data", {})

        logger.info(f"Received Lemon Squeezy webhook: {event_name}")

        if event_name == "subscription_created":
            await handle_subscription_created(data, subscription_service)
        elif event_name == "subscription_updated":
            await handle_subscription_updated(data, subscription_service)
        elif event_name == "subscription_cancelled":
            await handle_subscription_cancelled(data, subscription_service)
        elif event_name == "subscription_payment_success":
            await handle_payment_success(data, subscription_service)
        elif event_name == "subscription_payment_failed":
            await handle_payment_failed(data, subscription_service)
        elif event_name == "subscription_plan_changed":
            await handle_plan_changed(data, subscription_service)
        else:
            logger.info(f"Unhandled webhook event: {event_name}")

        return JSONResponse(content={"status": "success"})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook",
        )


async def handle_subscription_created(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        
        # Try both user_id and customer_id (LemonSqueezy uses customer_id)
        user_id_raw = attributes.get("user_id") or attributes.get("customer_id")
        if not user_id_raw:
            logger.error(f"Missing user_id/customer_id in subscription created event: {data.get('id')}")
            raise HTTPException(status_code=400, detail="Missing user identifier")
        
        import uuid

        try:
            if user_id_raw.startswith("cus_"):
                # Generate a UUID from the customer_id by hashing
                import hashlib
                hash_obj = hashlib.md5(user_id_raw.encode())
                user_id = str(uuid.UUID(hash_obj.hexdigest()))
            else:
                # Try to parse as UUID directly
                user_id = str(uuid.UUID(user_id_raw))
        except Exception as e:
            logger.error(f"Error converting user_id/customer_id to UUID: {e}")
            raise HTTPException(status_code=400, detail="Invalid user identifier format")
        
        # Parse dates with fallbacks
        from datetime import datetime, timedelta
        
        created_at_str = attributes.get("created_at")
        renews_at_str = attributes.get("renews_at")
        
        created_at = None
        renews_at = None
        
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error parsing created_at '{created_at_str}': {e}")
        if renews_at_str:
            try:
                renews_at = datetime.fromisoformat(renews_at_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error parsing renews_at '{renews_at_str}': {e}")
        
        # If both dates missing, fallback to utcnow and utcnow + 30 days
        if not created_at and not renews_at:
            created_at = datetime.utcnow()
            renews_at = created_at + timedelta(days=30)
        # If only one is missing, do not guess or fill to avoid incorrect data
        # current_period_start -> created_at
        # current_period_end -> renews_at
        
        # Check if user exists, if not create one
        existing_user = await service.get_user_by_id(user_id)
        if not existing_user:
            logger.info(f"User {user_id} not found, creating new user for subscription")
            # Use user_email from payload if available, otherwise placeholder
            user_email = attributes.get("user_email") or f"user_{user_id[:8]}@lemonsqueezy.local"
            created_user = await service.create_user(email=user_email, auth_provider_id=user_id)
            # Update user_id to use the actual database ID
            user_id = str(created_user.id)
            logger.info(f"Created user {created_user.id} with email {user_email}")
            logger.info(f"User object: {created_user}")
            logger.info(f"Database connection: {service.db_pool}")
        
        subscription_data = SubscriptionCreate(
            user_id=user_id,
            external_id=str(data.get("id")),
            provider=PaymentProvider.LEMON_SQUEEZY,
            plan=attributes.get("variant_name", "pro").lower(),
            status=SubscriptionStatus.ACTIVE
            if attributes.get("status") == "active"
            else SubscriptionStatus.INACTIVE,
            current_period_start=created_at or datetime.utcnow(),
            current_period_end=renews_at,
            trial_start=None,  # Simplified for now
            trial_end=None,    # Simplified for now
        )
        # Check if subscription already exists
        existing_subscription = await service.get_subscription_by_external_id(
            PaymentProvider.LEMON_SQUEEZY, str(data.get("id"))
        )
        
        if existing_subscription:
            logger.info(f"Subscription {data.get('id')} already exists, updating...")
            # Update existing subscription
            from backend.models.subscription import SubscriptionUpdate
            update_data = SubscriptionUpdate(
                status=subscription_data.status,
                current_period_start=subscription_data.current_period_start,
                current_period_end=subscription_data.current_period_end,
            )
            await service.update_subscription(str(existing_subscription.id), update_data)
            logger.info(f"Updated subscription: {data.get('id')}")
        else:
            await service.create_subscription(subscription_data)
            logger.info(f"Created subscription: {data.get('id')}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Error in handle_subscription_created")


async def handle_subscription_updated(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        external_id = str(data.get("id"))
        status = (
            SubscriptionStatus.ACTIVE
            if attributes.get("status") == "active"
            else SubscriptionStatus.INACTIVE
        )
        await service.update_subscription_status(external_id, status)
        logger.info(f"Updated subscription: {external_id}")
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(status_code=500, detail="Error in handle_subscription_updated")


async def handle_subscription_cancelled(
    data: Dict[str, Any], service: SubscriptionService
):
    try:
        external_id = str(data.get("id"))
        await service.update_subscription_status(external_id, SubscriptionStatus.CANCELLED)
        logger.info(f"Cancelled subscription: {external_id}")
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail="Error in handle_subscription_cancelled")


async def handle_payment_success(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")
        if subscription_id:
            amount = attributes.get("amount")
            currency = attributes.get("currency")
            invoice_id = attributes.get("invoice_id")
            await service.record_payment_event(subscription_id, amount, currency, invoice_id)
            await service.update_subscription_status(
                str(subscription_id), SubscriptionStatus.ACTIVE
            )
            logger.info(f"Payment success for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")
        raise HTTPException(status_code=500, detail="Error in handle_payment_success")


async def handle_payment_failed(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")
        if subscription_id:
            await service.update_subscription_status(
                str(subscription_id), SubscriptionStatus.PAST_DUE
            )
            logger.info(f"Payment failed for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")
        raise HTTPException(status_code=500, detail="Error in handle_payment_failed")


async def handle_plan_changed(data: Dict[str, Any], service: SubscriptionService):
    try:
        attributes = data.get("attributes", {})
        external_id = str(data.get("id"))
        new_plan = attributes.get("variant_id") or attributes.get("variant_name", "pro")
        new_plan = str(new_plan).lower()
        await service.update_subscription_plan(external_id, new_plan)
        logger.info(f"Plan changed for subscription: {external_id} to {new_plan}")
    except Exception as e:
        logger.error(f"Error handling plan change: {e}")
        raise HTTPException(status_code=500, detail="Error in handle_plan_changed")


__all__ = ["router"]
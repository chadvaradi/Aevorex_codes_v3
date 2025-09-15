
"""
Lemon Squeezy Webhook Handler
============================

Handles webhook events from Lemon Squeezy for subscription management.
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from modules.financehub.backend.core.services.subscription_service import get_subscription_service, SubscriptionService
from modules.financehub.backend.models.subscription import SubscriptionCreate, SubscriptionStatus, PaymentProvider

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_webhook_signature(request: Request, webhook_secret: str) -> bool:
    """
    Verify the webhook signature from Lemon Squeezy.
    
    Args:
        request: FastAPI request object
        webhook_secret: The webhook signing secret from Lemon Squeezy
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Get the signature from headers
        signature = request.headers.get("x-signature")
        if not signature:
            logger.warning("No signature found in webhook headers")
            return False
            
        # Get the raw body
        body = request.body()
        
        # Create expected signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False


@router.post("/lemonsqueezy")
async def handle_lemonsqueezy_webhook(
    request: Request,
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Handle Lemon Squeezy webhook events.
    
    Supported events:
    - subscription_created
    - subscription_updated
    - subscription_cancelled
    - subscription_payment_success
    - subscription_payment_failed
    - subscription_plan_changed
    """
    
    # Get webhook secret from environment
    import os
    webhook_secret = os.getenv("LEMON_SQUEEZY_WEBHOOK_SECRET")
    
    if not webhook_secret:
        logger.error("LEMON_SQUEEZY_WEBHOOK_SECRET not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )
    
    # Verify webhook signature
    if not verify_webhook_signature(request, webhook_secret):
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    try:
        # Parse webhook payload
        payload = await request.json()
        event_name = payload.get("meta", {}).get("event_name")
        data = payload.get("data", {})
        
        logger.info(f"Received Lemon Squeezy webhook: {event_name}")
        
        # Handle different event types
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
            detail="Error processing webhook"
        )


async def handle_subscription_created(data: Dict[str, Any], service: SubscriptionService):
    """Handle subscription_created event."""
    try:
        attributes = data.get("attributes", {})
        
        subscription_data = SubscriptionCreate(
            user_id=attributes.get("user_id"),
            external_id=str(data.get("id")),
            provider=PaymentProvider.LEMON_SQUEEZY,
            plan=attributes.get("variant_name", "pro").lower(),
            status=SubscriptionStatus.ACTIVE if attributes.get("status") == "active" else SubscriptionStatus.INACTIVE,
            current_period_start=attributes.get("renews_at"),
            current_period_end=attributes.get("ends_at"),
            trial_start=attributes.get("trial_starts_at"),
            trial_end=attributes.get("trial_ends_at")
        )
        
        await service.create_subscription(subscription_data)
        logger.info(f"Created subscription: {data.get('id')}")
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")


async def handle_subscription_updated(data: Dict[str, Any], service: SubscriptionService):
    """Handle subscription_updated event."""
    try:
        attributes = data.get("attributes", {})
        external_id = str(data.get("id"))
        
        # Update subscription status
        status = SubscriptionStatus.ACTIVE if attributes.get("status") == "active" else SubscriptionStatus.INACTIVE
        
        await service.update_subscription_status(external_id, status)
        logger.info(f"Updated subscription: {external_id}")
        
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")


async def handle_subscription_cancelled(data: Dict[str, Any], service: SubscriptionService):
    """Handle subscription_cancelled event."""
    try:
        external_id = str(data.get("id"))
        
        await service.update_subscription_status(external_id, SubscriptionStatus.CANCELLED)
        logger.info(f"Cancelled subscription: {external_id}")
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")


async def handle_payment_success(data: Dict[str, Any], service: SubscriptionService):
    """Handle subscription_payment_success event."""
    try:
        attributes = data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")
        
        if subscription_id:
            await service.update_subscription_status(str(subscription_id), SubscriptionStatus.ACTIVE)
            logger.info(f"Payment success for subscription: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")


async def handle_payment_failed(data: Dict[str, Any], service: SubscriptionService):
    """Handle subscription_payment_failed event."""
    try:
        attributes = data.get("attributes", {})
        subscription_id = attributes.get("subscription_id")
        
        if subscription_id:
            await service.update_subscription_status(str(subscription_id), SubscriptionStatus.PAST_DUE)
            logger.info(f"Payment failed for subscription: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")


async def handle_plan_changed(data: Dict[str, Any], service: SubscriptionService):
    """Handle subscription_plan_changed event."""
    try:
        attributes = data.get("attributes", {})
        external_id = str(data.get("id"))
        new_plan = attributes.get("variant_name", "pro").lower()
        
        await service.update_subscription_plan(external_id, new_plan)
        logger.info(f"Plan changed for subscription: {external_id} to {new_plan}")
        
    except Exception as e:
        logger.error(f"Error handling plan change: {e}")




import logging
import hmac
import hashlib
import base64
from fastapi import APIRouter, Request, HTTPException, status, Header
from fastapi.responses import JSONResponse
from backend.core.services.subscription_service import get_subscription_service, SubscriptionService
from backend.models.subscription import SubscriptionCreate, SubscriptionStatus, PaymentProvider

router = APIRouter()
logger = logging.getLogger(__name__)

import os
LEMONSQUEEZY_SIGNATURE_HEADER = "X-Signature"
LEMONSQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verifies the Lemon Squeezy webhook signature.
    """
    if not LEMONSQUEEZY_WEBHOOK_SECRET:
        logger.error("Lemon Squeezy webhook secret not set")
        return False
    computed_hmac = hmac.new(
        LEMONSQUEEZY_WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()
    # Lemon Squeezy sends the signature as a hex digest
    valid = hmac.compare_digest(computed_hmac, signature)
    if not valid:
        logger.warning("Lemon Squeezy webhook signature verification failed")
    return valid


@router.post("/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None, convert_underscores=False),
):
    """
    Lemon Squeezy webhook endpoint. Verifies signature and dispatches event handlers.
    """
    raw_body = await request.body()
    if not x_signature or not verify_webhook_signature(raw_body, x_signature):
        logger.warning("Unauthorized Lemon Squeezy webhook call")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse Lemon Squeezy webhook payload: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")

    event_type = payload.get("meta", {}).get("event_name")
    logger.info(f"Lemon Squeezy webhook event: {event_type}")
    try:
        if event_type == "subscription_created":
            await handle_subscription_created(payload)
        elif event_type == "subscription_updated":
            await handle_subscription_updated(payload)
        elif event_type == "subscription_cancelled":
            await handle_subscription_cancelled(payload)
        elif event_type == "subscription_payment_success":
            await handle_payment_success(payload)
        elif event_type == "subscription_payment_failed":
            await handle_payment_failed(payload)
        elif event_type == "subscription_plan_changed":
            await handle_plan_changed(payload)
        else:
            logger.warning(f"Unhandled Lemon Squeezy event: {event_type}")
    except Exception as e:
        logger.exception(f"Error handling Lemon Squeezy event {event_type}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return JSONResponse(content={"status": "ok"})


async def handle_subscription_created(payload: dict):
    """
    Handles Lemon Squeezy subscription_created event.
    """
    logger.info("Handling Lemon Squeezy subscription_created event")
    data = payload.get("data", {}).get("attributes", {})
    # You would extract user and subscription details from the payload here
    # Example:
    # user_id = data.get("user_id")
    # subscription_id = data.get("id")
    # Implement your logic here
    logger.debug(f"subscription_created data: {data}")


async def handle_subscription_updated(payload: dict):
    """
    Handles Lemon Squeezy subscription_updated event.
    """
    logger.info("Handling Lemon Squeezy subscription_updated event")
    data = payload.get("data", {}).get("attributes", {})
    logger.debug(f"subscription_updated data: {data}")
    # Implement your logic here


async def handle_subscription_cancelled(payload: dict):
    """
    Handles Lemon Squeezy subscription_cancelled event.
    """
    logger.info("Handling Lemon Squeezy subscription_cancelled event")
    data = payload.get("data", {}).get("attributes", {})
    logger.debug(f"subscription_cancelled data: {data}")
    # Implement your logic here


async def handle_payment_success(payload: dict):
    """
    Handles Lemon Squeezy subscription_payment_success event.
    """
    logger.info("Handling Lemon Squeezy subscription_payment_success event")
    data = payload.get("data", {}).get("attributes", {})
    logger.debug(f"payment_success data: {data}")
    # Implement your logic here


async def handle_payment_failed(payload: dict):
    """
    Handles Lemon Squeezy subscription_payment_failed event.
    """
    logger.info("Handling Lemon Squeezy subscription_payment_failed event")
    data = payload.get("data", {}).get("attributes", {})
    logger.debug(f"payment_failed data: {data}")
    # Implement your logic here


async def handle_plan_changed(payload: dict):
    """
    Handles Lemon Squeezy subscription_plan_changed event.
    """
    logger.info("Handling Lemon Squeezy subscription_plan_changed event")
    data = payload.get("data", {}).get("attributes", {})
    logger.debug(f"plan_changed data: {data}")
    # Implement your logic here
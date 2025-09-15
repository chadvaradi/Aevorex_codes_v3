"""
Checkout Tracking Service for Lemon Squeezy Integration
======================================================

Handles checkout session tracking and webhook correlation.
"""

import logging
from typing import Optional, Dict, Any
from asyncpg import Pool

logger = logging.getLogger(__name__)


class CheckoutTrackingService:
    """Service for tracking checkout sessions and correlating webhook events."""

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool

    async def create_checkout_session(
        self, checkout_id: str, user_id: str, variant_id: str
    ) -> Dict[str, Any]:
        """Create a new checkout tracking session."""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    INSERT INTO checkout_tracking (checkout_id, user_id, variant_id, status)
                    VALUES ($1, $2, $3, 'pending')
                    RETURNING id, checkout_id, user_id, variant_id, status, created_at
                """
                row = await conn.fetchrow(query, checkout_id, user_id, variant_id)

                logger.info(
                    f"Created checkout session: {checkout_id} for user {user_id}"
                )
                return dict(row)

        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise

    async def get_checkout_by_id(self, checkout_id: str) -> Optional[Dict[str, Any]]:
        """Get checkout session by checkout ID."""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT id, checkout_id, user_id, variant_id, status, 
                           created_at, updated_at, webhook_processed_at, webhook_event_id
                    FROM checkout_tracking 
                    WHERE checkout_id = $1
                """
                row = await conn.fetchrow(query, checkout_id)
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting checkout by ID: {e}")
            raise

    async def update_checkout_status(
        self, checkout_id: str, status: str, webhook_event_id: Optional[str] = None
    ) -> bool:
        """Update checkout status (for webhook processing)."""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    UPDATE checkout_tracking 
                    SET status = $2, 
                        webhook_processed_at = NOW(),
                        webhook_event_id = COALESCE($3, webhook_event_id)
                    WHERE checkout_id = $1
                    RETURNING id
                """
                row = await conn.fetchrow(query, checkout_id, status, webhook_event_id)

                if row:
                    logger.info(f"Updated checkout {checkout_id} status to {status}")
                    return True
                else:
                    logger.warning(
                        f"Checkout {checkout_id} not found for status update"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error updating checkout status: {e}")
            raise

    async def get_pending_checkouts_by_user(self, user_id: str) -> list[Dict[str, Any]]:
        """Get all pending checkouts for a user."""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT id, checkout_id, user_id, variant_id, status, created_at
                    FROM checkout_tracking 
                    WHERE user_id = $1 AND status = 'pending'
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, user_id)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting pending checkouts for user: {e}")
            raise

    async def cleanup_old_pending_checkouts(self, hours: int = 24) -> int:
        """Clean up old pending checkouts (for maintenance)."""
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    UPDATE checkout_tracking 
                    SET status = 'cancelled'
                    WHERE status = 'pending' 
                    AND created_at < NOW() - INTERVAL '$1 hours'
                    RETURNING id
                """
                rows = await conn.fetch(query, hours)
                count = len(rows)

                if count > 0:
                    logger.info(f"Cleaned up {count} old pending checkouts")

                return count

        except Exception as e:
            logger.error(f"Error cleaning up old checkouts: {e}")
            raise


# Global instance
_checkout_tracking_service: Optional[CheckoutTrackingService] = None


def get_checkout_tracking_service() -> CheckoutTrackingService:
    """Get global checkout tracking service instance."""
    global _checkout_tracking_service
    if _checkout_tracking_service is None:
        from ....app_factory import main_db_pool

        _checkout_tracking_service = CheckoutTrackingService(main_db_pool)
    return _checkout_tracking_service

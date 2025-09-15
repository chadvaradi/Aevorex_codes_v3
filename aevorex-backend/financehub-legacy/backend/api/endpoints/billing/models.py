

"""
Pydantic models for Lemon Squeezy billing and webhook events.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class LemonSqueezyMeta(BaseModel):
    event_name: str


class LemonSqueezyAttributes(BaseModel):
    user_id: Optional[str] = None
    status: Optional[str] = None
    variant_name: Optional[str] = None
    renews_at: Optional[str] = None
    ends_at: Optional[str] = None
    trial_starts_at: Optional[str] = None
    trial_ends_at: Optional[str] = None
    subscription_id: Optional[str] = None


class LemonSqueezyData(BaseModel):
    id: str
    attributes: LemonSqueezyAttributes


class LemonSqueezyWebhook(BaseModel):
    meta: LemonSqueezyMeta
    data: LemonSqueezyData
    additional: Dict[str, Any] = {}
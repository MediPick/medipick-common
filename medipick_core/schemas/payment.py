"""Shared payment schemas and webhook definitions."""
from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict


class WebhookEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["payment_intent.succeeded", "payment_intent.payment_failed", "payment_intent.refunded"]
    data: dict


class MockConfirmPaymentBody(BaseModel):
    orderId: uuid.UUID

"""
MediPick Core — Shared Payment Schemas & Webhook Definitions.
"""
from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CreatePaymentIntentBody(BaseModel):
    orderId: uuid.UUID
    paymentMethod: Literal["ONLINE"]


class PaymentIntentOut(BaseModel):
    paymentIntentId: str
    clientSecret: str
    amount: float
    currency: Literal["LKR"]
    gateway: str
    orderId: str


class WebhookEventData(BaseModel):
    intentId: str


class WebhookEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["payment_intent.succeeded", "payment_intent.payment_failed", "payment_intent.refunded"]
    data: WebhookEventData | dict


class MockConfirmPaymentBody(BaseModel):
    orderId: uuid.UUID


class WebhookAck(BaseModel):
    received: bool = True

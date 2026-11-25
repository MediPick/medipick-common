"""
MediPick — Payment Service
Creates payment intents and processes gateway webhooks.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from medipick_core.exceptions import MediPickException
from medipick_core.models.customer import Customer
from medipick_core.models.notification import NotificationType
from medipick_core.models.order import Order, OrderState, PaymentMethod
from medipick_core.models.payment import PaymentStatus, PaymentTransaction
from medipick_core.models.quote import Quote, QuoteStatus
from medipick_core.schemas.payment import WebhookEvent
from medipick_core.services.notification_service import notification_service

logger = logging.getLogger(__name__)

PAYABLE_STATES = {
    OrderState.SUBMITTED,
    OrderState.WAITING_PHARMACY_CONFIRMATION,
    OrderState.WAITING_CUSTOMER_CONFIRMATION,
    OrderState.PREPARING,
    OrderState.READY_FOR_PICKUP,
}


class MockPaymentGateway:
    name = "mock"

    def create_intent(self, amount: float, currency: str, reference: str) -> tuple[str, str]:
        intent_id = f"pi_mock_{uuid.uuid4().hex[:24]}"
        return intent_id, f"{intent_id}_secret_{secrets.token_urlsafe(16)}"

    def refund(self, intent_id: str, amount: float) -> None:
        logger.info("[mock gateway] refunded %s LKR on %s", amount, intent_id)


def _build_gateway():
    gw = os.getenv("PAYMENT_GATEWAY", "mock")
    if gw == "mock":
        return MockPaymentGateway()
    raise RuntimeError(f"Unknown PAYMENT_GATEWAY '{gw}'")


class PaymentService:

    def __init__(self) -> None:
        self.gateway = _build_gateway()

    def verify_webhook_signature(self, raw_body: bytes, signature_header: str | None) -> None:
        secret = os.getenv("PAYMENT_WEBHOOK_SECRET", "dev-webhook-secret")
        if not signature_header or not signature_header.startswith("sha256="):
            raise MediPickException("INVALID_SIGNATURE", 401, "Missing or malformed X-MediPick-Signature.")
        provided = signature_header.removeprefix("sha256=")
        expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(provided, expected):
            raise MediPickException("INVALID_SIGNATURE", 401, "Webhook signature mismatch.")

    async def create_payment_intent(
        self, db: AsyncSession, order_id: uuid.UUID, customer_user_id: uuid.UUID
    ) -> tuple[Order, str, str]:
        order = await self._load_order_for_payment(db, order_id, customer_user_id)
        if order.is_paid:
            raise MediPickException("ALREADY_PAID", 409, "This order is already paid.")
        if order.payment_method != PaymentMethod.ONLINE:
            raise MediPickException(
                "INVALID_PAYMENT_METHOD", 400,
                f"Order was placed with {order.payment_method.value}; online payment not allowed.",
            )
        if order.state not in PAYABLE_STATES:
            raise MediPickException(
                "ORDER_NOT_PAYABLE", 409,
                f"Orders in state {order.state.value} cannot be paid.",
            )

        amount = float(order.total_amount)
        if amount <= 0:
            raise MediPickException("INVALID_AMOUNT", 400, "Order total must be greater than zero.")

        intent_id, client_secret = self.gateway.create_intent(
            amount=amount, currency="LKR", reference=order.order_number
        )

        txn = PaymentTransaction(
            order_id=order.id,
            gateway=self.gateway.name,
            gateway_intent_id=intent_id,
            amount=amount,
            currency="LKR",
            status=PaymentStatus.PENDING,
        )
        db.add(txn)
        await db.flush()
        return order, intent_id, client_secret

    async def process_webhook(self, db: AsyncSession, event: WebhookEvent) -> None:
        intent_id = event.data.get("intentId")
        if not intent_id:
            logger.warning("Ignoring webhook event %s without intentId", event.type)
            return

        result = await db.execute(
            select(PaymentTransaction).where(PaymentTransaction.gateway_intent_id == intent_id)
        )
        txn = result.scalar_one_or_none()
        if txn is None:
            logger.warning("Webhook references unknown intent %s", intent_id)
            return

        if txn.status in (PaymentStatus.SUCCEEDED, PaymentStatus.REFUNDED):
            return

        order_res = await db.execute(select(Order).where(Order.id == txn.order_id))
        order = order_res.scalar_one_or_none()

        if event.type == "payment_intent.succeeded":
            txn.status = PaymentStatus.SUCCEEDED
            txn.gateway_charge_id = event.data.get("chargeId")
            if order:
                order.is_paid = True
                order.payment_method = PaymentMethod.ONLINE
                await notification_service.notify_customer(
                    db,
                    order.customer_id,
                    NotificationType.PAYMENT_SUCCESSFUL,
                    "Payment confirmed",
                    f"Payment of LKR {txn.amount:.2f} for order {order.order_number} was received.",
                    order_id=order.id,
                )
        elif event.type == "payment_intent.payment_failed":
            txn.status = PaymentStatus.FAILED
            txn.error_code = event.data.get("errorCode")
            txn.error_message = event.data.get("errorMessage")
            if order:
                await notification_service.notify_customer(
                    db,
                    order.customer_id,
                    NotificationType.ORDER_STATUS_CHANGED,
                    "Payment failed",
                    f"Payment for order {order.order_number} could not be processed. Tap to retry.",
                    order_id=order.id,
                )
        elif event.type == "payment_intent.refunded":
            txn.status = PaymentStatus.REFUNDED
            if order:
                order.refund_status = "REFUNDED"
                order.refund_amount = float(txn.amount)

        await db.flush()

    async def refund_order(self, db: AsyncSession, order: Order) -> None:
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.order_id == order.id,
                PaymentTransaction.status == PaymentStatus.SUCCEEDED,
            )
        )
        txn = result.scalar_one_or_none()
        if txn is None:
            return

        self.gateway.refund(txn.gateway_intent_id, float(txn.amount))
        txn.status = PaymentStatus.REFUNDED
        order.refund_status = "REFUNDED"
        order.refund_amount = float(txn.amount)
        await db.flush()

        await notification_service.notify_customer(
            db,
            order.customer_id,
            NotificationType.ORDER_STATUS_CHANGED,
            "Refund issued",
            f"LKR {txn.amount:.2f} for order {order.order_number} was refunded to your card.",
            order_id=order.id,
        )

    async def _load_order_for_payment(
        self, db: AsyncSession, order_id: uuid.UUID, customer_user_id: uuid.UUID
    ) -> Order:
        result = await db.execute(
            select(Order, Customer)
            .join(Customer, Order.customer_id == Customer.id)
            .where(Order.id == order_id, Customer.user_id == customer_user_id)
        )
        row = result.first()
        if row is None:
            raise MediPickException("NOT_FOUND", 404, "Order not found.")
        return row[0]


payment_service = PaymentService()

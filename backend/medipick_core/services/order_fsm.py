"""
MediPick — Order State Machine (Domain Service)
Every order state change goes through `transition()` so its side effects are
applied consistently across the entire platform.
"""
from __future__ import annotations

import os
from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from medipick_core.exceptions import MediPickException
from medipick_core.models.customer import Customer
from medipick_core.models.notification import NotificationType
from medipick_core.models.order import Order, OrderState, PaymentMethod
from medipick_core.models.quote import Quote, QuoteStatus
from medipick_core.security import generate_otp
from medipick_core.services.notification_service import notification_service
from medipick_core.services.payment_service import payment_service
from medipick_core.services.stock_service import stock_service
from medipick_core.utils.timeutil import utcnow

FREE_CANCEL_STATES = {
    OrderState.DRAFT,
    OrderState.SUBMITTED,
    OrderState.PRESCRIPTION_VALIDATION,
    OrderState.AWAITING_PRESCRIPTION_UPLOAD,
    OrderState.REUPLOAD_REQUESTED,
    OrderState.WAITING_PHARMACY_CONFIRMATION,
}
TERMINAL_STATES = {OrderState.COMPLETED, OrderState.CANCELLED, OrderState.CLOSED, OrderState.REJECTED}

_NOTIFICATIONS: dict[OrderState, tuple[NotificationType, str, str]] = {
    OrderState.WAITING_PHARMACY_CONFIRMATION: (
        NotificationType.ORDER_STATUS_CHANGED, "Sent to pharmacy",
        "Order {no} is with {pharmacy} for review.",
    ),
    OrderState.WAITING_CUSTOMER_CONFIRMATION: (
        NotificationType.QUOTE_RECEIVED, "Quote received",
        "{pharmacy} sent a price quote for order {no}. Review it before it expires.",
    ),
    OrderState.AWAITING_PRESCRIPTION_UPLOAD: (
        NotificationType.PRESCRIPTION_REJECTED, "Please re-upload your prescription",
        "The prescription for order {no} wasn't clear enough to read. Upload a sharper photo.",
    ),
    OrderState.PREPARING: (
        NotificationType.ORDER_STATUS_CHANGED, "Order is being prepared",
        "{pharmacy} is preparing order {no}.",
    ),
    OrderState.READY_FOR_PICKUP: (
        NotificationType.PICKUP_READY, "Ready for pickup",
        "Order {no} is ready at {pharmacy}. Show your pickup code at the counter.",
    ),
    OrderState.COMPLETED: (
        NotificationType.ORDER_STATUS_CHANGED, "Order completed",
        "Thanks for picking up order {no}! Tap to rate your experience.",
    ),
    OrderState.CANCELLED: (
        NotificationType.ORDER_CANCELLED, "Order cancelled",
        "Order {no} was cancelled.",
    ),
}


class OrderFSM:

    async def transition(
        self,
        db: AsyncSession,
        order: Order,
        new_state: OrderState,
        *,
        reason: str | None = None,
        notify: bool = True,
    ) -> None:
        if order.state == new_state:
            return
        now = utcnow()

        if new_state == OrderState.READY_FOR_PICKUP:
            pickup_hours = int(os.getenv("PICKUP_WINDOW_HOURS", "24"))
            order.pickup_code = generate_otp()
            order.pickup_code_verified = False
            order.pickup_deadline = now + timedelta(hours=pickup_hours)
            order.pickup_extension_requested = False
            order.pickup_extension_status = None
            order.pickup_failed_attempts = 0
            order.pickup_locked_until = None
            if order.ready_at is None:
                order.ready_at = now

        elif new_state == OrderState.COMPLETED:
            order.completed_at = now
            order.pickup_code_verified = True
            if order.payment_method != PaymentMethod.ONLINE:
                order.is_paid = True  # settled at the counter

        elif new_state == OrderState.CANCELLED:
            if hasattr(order, "items") and order.items:
                for it in order.items:
                    await stock_service.release(db, order.pharmacy_id, it)
            await db.execute(
                update(Quote)
                .where(Quote.order_id == order.id, Quote.status == QuoteStatus.PENDING)
                .values(status=QuoteStatus.EXPIRED)
            )
            if order.is_paid:
                await payment_service.refund_order(db, order)
                if order.payment_method != PaymentMethod.ONLINE and order.refund_status != "REFUNDED":
                    order.refund_status = "REFUNDED"
                    order.refund_amount = float(order.total_amount)
            if reason:
                order.reject_reason = reason

        order.state = new_state
        await db.flush()

        if notify and new_state in _NOTIFICATIONS:
            ntype, title, body = _NOTIFICATIONS[new_state]
            pharmacy_name = order.pharmacy.name if hasattr(order, "pharmacy") and order.pharmacy else "Pharmacy"
            text = body.format(no=order.order_number, pharmacy=pharmacy_name)
            if new_state == OrderState.CANCELLED and reason:
                text = f"{text} Reason: {reason}"
            await notification_service.notify_customer(
                db, order.customer_id, ntype, title, text, order_id=order.id,
            )

    async def cancel_by_customer(self, db: AsyncSession, order: Order, customer: Customer) -> int:
        if order.state in TERMINAL_STATES or order.state not in (
            FREE_CANCEL_STATES | {OrderState.WAITING_CUSTOMER_CONFIRMATION, OrderState.PREPARING}
        ):
            raise MediPickException(
                "ORDER_NOT_CANCELLABLE", 409,
                f"Orders in state {order.state.value} can no longer be cancelled.",
            )

        if await self._customer_already_committed(db, order):
            self.apply_strike(customer)

        await self.transition(db, order, OrderState.CANCELLED, reason="Cancelled by customer")
        return customer.no_show_count

    async def _customer_already_committed(self, db: AsyncSession, order: Order) -> bool:
        if order.state == OrderState.PREPARING:
            return True
        if order.state == OrderState.WAITING_CUSTOMER_CONFIRMATION:
            accepted = await db.execute(
                select(Quote.id).where(Quote.order_id == order.id, Quote.status == QuoteStatus.ACCEPTED)
            )
            return accepted.first() is not None
        return False

    @staticmethod
    def apply_strike(customer: Customer) -> None:
        lockout_hours = int(os.getenv("LOCKOUT_HOURS", "24"))
        customer.no_show_count += 1
        if customer.no_show_count >= customer.strike_limit:
            customer.is_locked = True
            customer.locked_until = utcnow() + timedelta(hours=lockout_hours)


order_fsm = OrderFSM()

__all__ = [
    "OrderFSM",
    "order_fsm",
    "FREE_CANCEL_STATES",
    "TERMINAL_STATES",
]

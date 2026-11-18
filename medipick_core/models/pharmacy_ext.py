"""
MediPick Pharmacy — pharmacy-owned extension tables.

Shared tables (pharmacies, inventory_items, quotes, order_ratings, issues) are
owned by the customer backend's schema and must not gain columns here. Extra
per-row data lives in these tables, keyed by the shared row's id.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from medipick_core.database import Base


def _ts():
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


def _uts():
    return mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PharmacySettings(Base):
    """Store configuration (1:1 with pharmacies)."""
    __tablename__ = "pharmacy_settings"

    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), primary_key=True,
    )
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weekly_hours: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    holidays: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    preferences: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    gallery_file_keys: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    storefront_file_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _uts()


class PharmacyBankDetails(Base):
    __tablename__ = "pharmacy_bank_details"

    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), primary_key=True,
    )
    bank_name: Mapped[str] = mapped_column(String(150), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(150), nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    passbook_file_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passbook_document_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    settlement_cycle: Mapped[str] = mapped_column(
        String(120), default="T+1 Daily Automated Clearing (SLIPS / CEFT)", nullable=False,
    )
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _uts()


class ComplianceDocument(Base):
    __tablename__ = "pharmacy_compliance_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    doc_type: Mapped[str] = mapped_column(String(40), nullable=False)  # nmra_license | business_registration | pharmacist_slmc | bank_passbook
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending_review", nullable=False)  # verified | pending_review | rejected
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _uts()


class Promotion(Base):
    __tablename__ = "pharmacy_promotions"
    __table_args__ = (UniqueConstraint("pharmacy_id", "code", name="uq_promotion_pharmacy_code"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(10), nullable=False)  # percent | flat
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    redemptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    promo_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict, nullable=True)
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _uts()


class InventoryItemMeta(Base):
    """Dispensary-only stock attributes for an inventory_items row."""
    __tablename__ = "inventory_item_meta"

    inventory_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), primary_key=True,
    )
    min_alert_threshold: Mapped[int] = mapped_column(SmallInteger, default=20, nullable=False)
    batch_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _uts()


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    inventory_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    created_at: Mapped[datetime] = _ts()


class QuoteMeta(Base):
    """Discount / promo applied to a quote. quotes.total_amount is already net of the discount."""
    __tablename__ = "quote_meta"

    quote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"), primary_key=True,
    )
    subtotal_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    promo_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = _ts()


class ReviewReply(Base):
    __tablename__ = "pharmacy_review_replies"

    order_rating_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order_ratings.id", ondelete="CASCADE"), primary_key=True,
    )
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    reply: Mapped[str] = mapped_column(Text, nullable=False)
    replied_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    created_at: Mapped[datetime] = _ts()
    updated_at: Mapped[datetime] = _uts()


class IssueResolution(Base):
    """Pharmacy-side handling of a customer issue (dispute)."""
    __tablename__ = "issue_resolutions"

    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), primary_key=True,
    )
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False)  # refund | replacement | rejected
    refund_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    refunded_item_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    pharmacist_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    created_at: Mapped[datetime] = _ts()


class AuditLog(Base):
    __tablename__ = "pharmacy_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    actor_name_snapshot: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_role_snapshot: Mapped[str | None] = mapped_column(String(60), nullable=True)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()


# ── Backward-compatibility aliases for legacy read-only imports ───────────────
from medipick_core.models.staff_profile import PharmacyStaffProfile

RoPharmacySettings = PharmacySettings
RoInventoryItemMeta = InventoryItemMeta
RoIssueResolution = IssueResolution
RoPromotion = Promotion
RoQuoteMeta = QuoteMeta
RoReviewReply = ReviewReply
RoPharmacyStaffProfile = PharmacyStaffProfile



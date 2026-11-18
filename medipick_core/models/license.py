"""
MediPick — Pharmacy License Model
Maps to the `pharmacy_licenses` table.

Records active and historical NMRA retail pharmacy licenses, valid date ranges,
and regulatory verification tracking.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medipick_core.database import Base

if TYPE_CHECKING:
    from medipick_core.models.pharmacy import Pharmacy
    from medipick_core.models.pharmacy_ext import ComplianceDocument
    from medipick_core.models.user import User


class PharmacyLicense(Base):
    __tablename__ = "pharmacy_licenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    licence_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacy_compliance_documents.id", ondelete="SET NULL"), nullable=True
    )

    verification_status: Mapped[str] = mapped_column(
        String(30), default="VERIFIED", nullable=False, comment="PENDING | VERIFIED | REJECTED | EXPIRED"
    )

    verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PharmacyLicense pharmacy={self.pharmacy_id} num={self.licence_number} status={self.verification_status}>"


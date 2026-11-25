"""
MediPick — Pharmacy Company ORM Model
Maps to the `pharmacy_companies` table.

Represents the legal corporate entity holding the Business Registration Number (BRN),
head office, and multi-branch ownership. One company can own 1 to N retail branches (pharmacies).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medipick_core.database import Base

if TYPE_CHECKING:
    from medipick_core.models.pharmacy import Pharmacy
    from medipick_core.models.user import User


class PharmacyCompany(Base):
    __tablename__ = "pharmacy_companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    business_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_registration_number: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True, comment="Company BRN e.g. PV 00456"
    )

    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    head_office_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    verification_status: Mapped[str] = mapped_column(
        String(30), default="APPROVED", nullable=False, comment="PENDING | APPROVED | REJECTED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    branches: Mapped[list["Pharmacy"]] = relationship(
        "Pharmacy", back_populates="company", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<PharmacyCompany id={self.id} name={self.business_name}>"


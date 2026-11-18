"""
MediPick — Pharmacist Profile & Responsible Pharmacist Assignment Models
Maps to `pharmacist_profiles` and `branch_pharmacist_assignments`.

Under NMRA Act No. 5 of 2015 & SLMC regulations:
- An SLMC registration belongs personally to the pharmacist, independent of employment.
- Section 120 requires appointment of a verified Responsible Pharmacist per physical retail outlet.
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
    from medipick_core.models.user import User


class PharmacistProfile(Base):
    __tablename__ = "pharmacist_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    slmc_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="SLMC Registration Number e.g. SLMC-PH-4412"
    )

    registration_status: Mapped[str] = mapped_column(
        String(30), default="ACTIVE", nullable=False, comment="ACTIVE | SUSPENDED | EXPIRED"
    )
    verification_status: Mapped[str] = mapped_column(
        String(30), default="VERIFIED", nullable=False, comment="PENDING | VERIFIED | REJECTED"
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    assignments: Mapped[list["BranchPharmacistAssignment"]] = relationship(
        "BranchPharmacistAssignment", back_populates="pharmacist", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<PharmacistProfile user_id={self.user_id} slmc={self.slmc_number}>"


class BranchPharmacistAssignment(Base):
    __tablename__ = "branch_pharmacist_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pharmacist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacist_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    appointment_type: Mapped[str] = mapped_column(
        String(50), default="RESPONSIBLE_PHARMACIST", nullable=False,
        comment="RESPONSIBLE_PHARMACIST | RELIEF_PHARMACIST | SUPERVISING_PHARMACIST"
    )

    start_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(
        String(30), default="ACTIVE", nullable=False, comment="ACTIVE | TERMINATED | ON_LEAVE"
    )

    supporting_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacy_compliance_documents.id", ondelete="SET NULL"), nullable=True
    )
    nmra_acknowledgement: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    pharmacist: Mapped["PharmacistProfile"] = relationship("PharmacistProfile", back_populates="assignments", lazy="selectin")

    def __repr__(self) -> str:
        return f"<BranchPharmacistAssignment pharmacy={self.pharmacy_id} type={self.appointment_type} status={self.status}>"


"""
MediPick Pharmacy — Staff profile (pharmacy-owned table).

One row per staff user (`users.role` PHARMACIST / PHARMACY_STAFF). The fine-
grained built-in role lives here as VARCHAR; permissions are NEVER stored —
they are always derived from `staff_role` (see app/core/rbac.py).
Each branch is its own `pharmacies` row, so a staff user belongs to exactly
one pharmacy (== users.pharmacy_id).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medipick_core.database import Base


class PharmacyStaffProfile(Base):
    __tablename__ = "pharmacy_staff_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "pharmacy_id", name="uq_staff_user_pharmacy"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True,
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    staff_role: Mapped[str] = mapped_column(String(60), nullable=False, comment="One of the 7 built-in roles.")
    slmc_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_designated_manager: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    on_duty: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shift: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Brute-force protection for password login.
    failed_login_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Password-reset OTP (bcrypt hash).
    reset_otp_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reset_otp_attempts: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<PharmacyStaffProfile {self.full_name} role={self.staff_role}>"


"""
MediPick — Favorite Medicine ORM Model
Maps to the `favorite_medicines` table.
One row per (customer, medicine) bookmark.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medipick_core.database import Base


class FavoriteMedicine(Base):
    __tablename__ = "favorite_medicines"
    __table_args__ = (
        UniqueConstraint("customer_id", "medicine_id", name="uq_favorite_customer_medicine"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    medicine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False, index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    medicine: Mapped["Medicine"] = relationship("Medicine", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<FavoriteMedicine id={self.id} customer_id={self.customer_id} medicine_id={self.medicine_id}>"


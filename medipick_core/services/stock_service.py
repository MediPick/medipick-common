"""
MediPick — Stock Service
Reserves pharmacy inventory when an order is placed and gives it back when the
order is cancelled. Inventory rows are locked (SELECT ... FOR UPDATE) so two
customers ordering the last unit at the same moment can't both get it.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from medipick_core.utils.timeutil import LOCAL_TZ, utcnow
from medipick_core.models.inventory_item import InventoryItem
from medipick_core.models.order import OrderItem
from medipick_core.models.pharmacy_ext import InventoryItemMeta


class StockService:

    async def lock_inventory(
        self, db: AsyncSession, pharmacy_id: uuid.UUID, medicine_id: uuid.UUID
    ) -> InventoryItem | None:
        result = await db.execute(
            select(InventoryItem)
            .where(InventoryItem.pharmacy_id == pharmacy_id, InventoryItem.medicine_id == medicine_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def is_item_available(self, db: AsyncSession, inventory: InventoryItem) -> bool:
        today_local = utcnow().astimezone(LOCAL_TZ).date()
        if inventory.expiry_date is not None and inventory.expiry_date < today_local:
            return False
        try:
            avail = (await db.execute(
                select(InventoryItemMeta.is_available).where(
                    InventoryItemMeta.inventory_item_id == inventory.id
                )
            )).scalar_one_or_none()
            if avail is False:
                return False
        except SQLAlchemyError:
            pass
        return True

    async def try_reserve(
        self, db: AsyncSession, pharmacy_id: uuid.UUID, item: OrderItem
    ) -> bool:
        """Best-effort reservation for an item whose price is already decided
        (e.g. from a pharmacist's quote). Never fails — just doesn't reserve."""
        if item.medicine_id is None:
            return False
        inventory = await self.lock_inventory(db, pharmacy_id, item.medicine_id)
        if inventory is None or inventory.stock_quantity < item.quantity:
            return False
        if not await self.is_item_available(db, inventory):
            return False

        inventory.stock_quantity -= item.quantity
        item.inventory_item_id = inventory.id
        return True

    async def release(
        self, db: AsyncSession, pharmacy_id: uuid.UUID, item: OrderItem
    ) -> None:
        """Restores inventory when an order is cancelled or rejected."""
        if item.inventory_item_id is None or item.medicine_id is None:
            return
        inventory = await self.lock_inventory(db, pharmacy_id, item.medicine_id)
        if inventory is not None:
            inventory.stock_quantity += item.quantity


stock_service = StockService()

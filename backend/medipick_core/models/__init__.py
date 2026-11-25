"""
MediPick Pharmacy — Models Package
Shared models are copied VERBATIM from medipick-customer-backend/app/models
(never add columns here); pharmacy-owned tables follow.
Import all models here so Alembic auto-detects them for migrations.
Order matters for FK resolution: User must come before Customer and RefreshToken.
"""
from medipick_core.models.user import User, UserRole
from medipick_core.models.customer import Customer
from medipick_core.models.refresh_token import RefreshToken
from medipick_core.models.pharmacy import Pharmacy, PharmacyStatus
from medipick_core.models.medicine_category import MedicineCategory
from medipick_core.models.medicine import Medicine
from medipick_core.models.inventory_item import InventoryItem
from medipick_core.models.favorite_pharmacy import FavoritePharmacy
from medipick_core.models.favorite_medicine import FavoriteMedicine
from medipick_core.models.prescription import Prescription, PrescriptionStatus
from medipick_core.models.order import Order, OrderItem, OrderRating, OrderState, OrderType, PaymentMethod
from medipick_core.models.quote import Quote, QuoteItem, QuoteStatus
from medipick_core.models.payment import PaymentStatus, PaymentTransaction
from medipick_core.models.chat import ChatMessage, ChatSession, SenderRole
from medipick_core.models.notification import Notification, NotificationType
from medipick_core.models.health_tip import HealthTip
from medipick_core.models.issue import Issue, IssueStatus, IssueType

# ── Pharmacy-owned tables ──────────────────────────────────────────────────────
from medipick_core.models.company import PharmacyCompany
from medipick_core.models.pharmacist import PharmacistProfile, BranchPharmacistAssignment
from medipick_core.models.license import PharmacyLicense
from medipick_core.models.staff_profile import PharmacyStaffProfile
from medipick_core.models.product_request import PharmacySupportTicket, ProductRequest, ProductRequestMessage
from medipick_core.models.pharmacy_ext import (
    AuditLog, ComplianceDocument, InventoryItemMeta, IssueResolution, PharmacyBankDetails,
    PharmacySettings, Promotion, QuoteMeta, ReviewReply, StockMovement,
    RoPharmacySettings, RoInventoryItemMeta, RoIssueResolution, RoPromotion,
    RoQuoteMeta, RoReviewReply, RoPharmacyStaffProfile,
)

__all__ = [
    "User", "UserRole", "Customer", "RefreshToken",
    "Pharmacy", "PharmacyStatus", "MedicineCategory", "Medicine", "InventoryItem",
    "FavoritePharmacy", "FavoriteMedicine",
    "Prescription", "PrescriptionStatus",
    "Order", "OrderItem", "OrderRating", "OrderState", "OrderType", "PaymentMethod",
    "Quote", "QuoteItem", "QuoteStatus",
    "PaymentTransaction", "PaymentStatus",
    "ChatSession", "ChatMessage", "SenderRole",
    "Notification", "NotificationType",
    "HealthTip",
    "Issue", "IssueStatus", "IssueType",
    "PharmacyCompany", "PharmacistProfile", "BranchPharmacistAssignment", "PharmacyLicense",
    "PharmacyStaffProfile", "AuditLog", "ComplianceDocument", "InventoryItemMeta", "IssueResolution",
    "PharmacyBankDetails", "PharmacySettings", "Promotion", "QuoteMeta", "ReviewReply", "StockMovement",
    "RoPharmacySettings", "RoInventoryItemMeta", "RoIssueResolution", "RoPromotion",
    "RoQuoteMeta", "RoReviewReply", "RoPharmacyStaffProfile",
]


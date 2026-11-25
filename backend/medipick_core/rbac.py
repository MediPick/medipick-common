"""
MediPick Core — Role-Based Access Control (RBAC) & Pharmacy Staff Roles.

Canonical definitions of the 7 dispensary staff roles, permissions, and validation helpers.
Used across pharmacy services, customer chat authorization, and staff authentication.
"""
from __future__ import annotations

from medipick_core.models.user import UserRole

# Canonical 7 built-in staff roles
OWNER_CHIEF = "Owner / Chief Pharmacist"
PHARMACY_OWNER = "Pharmacy Owner"
INVESTOR = "Investor"
DESIGNATED_MANAGER = "Designated Manager / Pharmacist"
STAFF_PHARMACIST = "Staff Pharmacist"
ASSISTANT = "Dispensary Assistant"
CASHIER = "Dispensary Cashier"

CANONICAL_ROLES: tuple[str, ...] = (
    OWNER_CHIEF,
    PHARMACY_OWNER,
    INVESTOR,
    DESIGNATED_MANAGER,
    STAFF_PHARMACIST,
    ASSISTANT,
    CASHIER,
)

PERMISSION_KEYS: tuple[str, ...] = (
    "canReviewRx",
    "canApproveQuotes",
    "canManageInventory",
    "canViewFinancials",
    "canManageStaff",
    "canProcessRefunds",
)


def _p(rx: bool, quotes: bool, inv: bool, fin: bool, staff: bool, refunds: bool) -> dict[str, bool]:
    return dict(zip(PERMISSION_KEYS, (rx, quotes, inv, fin, staff, refunds)))


ROLE_PERMISSIONS: dict[str, dict[str, bool]] = {
    OWNER_CHIEF:        _p(True,  True,  True,  True,  True,  True),
    PHARMACY_OWNER:     _p(False, False, True,  True,  True,  True),
    INVESTOR:           _p(False, False, False, True,  False, False),
    DESIGNATED_MANAGER: _p(True,  True,  True,  False, True,  True),
    STAFF_PHARMACIST:   _p(True,  True,  True,  False, False, True),
    ASSISTANT:          _p(False, False, True,  False, False, False),
    CASHIER:            _p(False, False, False, False, False, False),
}

ROLE_DESCRIPTIONS: dict[str, str] = {
    OWNER_CHIEF: "Executive & clinical authority. Full access: Financials, Staff, Clinical Rx, Inventory.",
    PHARMACY_OWNER: "Active non-pharmacist store owner. Financials, payouts, staff roster, store settings, and adding products/stock. (No clinical Rx review).",
    INVESTOR: "Silent financial stakeholder. Read-only access to gross revenue, payouts & analytics only. (No stock, staff, or Rx access).",
    DESIGNATED_MANAGER: "Branch operational lead. Rostering, inventory intake, dispute claims, and clinical Rx validation.",
    STAFF_PHARMACIST: "Certified dispenser. Validates Rx, OCR clarity, medicine quotes, patient chat, stock adjustments.",
    ASSISTANT: "Supports prescription assembly, picking & packing, batch entry, and stock threshold monitoring.",
    CASHIER: "Counter POS custody. Verifies 6-digit pickup PIN, collects payments, and releases packaged orders safely.",
}

SLMC_ROLES = {OWNER_CHIEF, DESIGNATED_MANAGER, STAFF_PHARMACIST}
CUSTODY_ROLES = {OWNER_CHIEF, DESIGNATED_MANAGER}      # Pharmacist-in-Charge capable
OWNER_ROLES = {OWNER_CHIEF, PHARMACY_OWNER}            # isOwnerRole()
MANAGER_ROLES = {DESIGNATED_MANAGER}                   # isDesignatedManagerRole()

LEGACY_ROLE_MAP: dict[str, str] = {
    "Pharmacy Owner / Director": PHARMACY_OWNER,
    "Pharmacy Owner / Manager": OWNER_CHIEF,
    "Chief Pharmacist": OWNER_CHIEF,
    "Designated Manager": DESIGNATED_MANAGER,
    "Supervising Pharmacist": STAFF_PHARMACIST,
    "Dispensary Assistant / Packer": ASSISTANT,
    "Dispensary Packer": ASSISTANT,
}


def normalize_role(role: str | None) -> str | None:
    """Returns the canonical role for `role` (accepting legacy aliases) or None."""
    role = (role or "").strip()
    if role in ROLE_PERMISSIONS:
        return role
    return LEGACY_ROLE_MAP.get(role)


def permissions_for(role: str) -> dict[str, bool]:
    canonical = normalize_role(role)
    return dict(ROLE_PERMISSIONS[canonical]) if canonical else dict.fromkeys(PERMISSION_KEYS, False)


def requires_slmc(role: str) -> bool:
    return normalize_role(role) in SLMC_ROLES


def is_owner_role(role: str) -> bool:
    return normalize_role(role) in OWNER_ROLES


def is_manager_role(role: str) -> bool:
    return normalize_role(role) in MANAGER_ROLES


def user_role_for(role: str) -> UserRole:
    """Coarse `users.role` (native PG enum) — SLMC roles are PHARMACIST."""
    return UserRole.PHARMACIST if requires_slmc(role) else UserRole.PHARMACY_STAFF

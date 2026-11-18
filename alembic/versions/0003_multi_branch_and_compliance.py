"""multi_branch_and_compliance

Revision ID: 0003_multi_branch_and_compliance
Revises: 0002_add_promotion_metadata
Create Date: 2026-11-16 20:15:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0003_multi_branch_and_compliance'
down_revision: Union[str, None] = '0002_add_promotion_metadata'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Create pharmacy_companies table ────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS pharmacy_companies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            business_name VARCHAR(255) NOT NULL,
            business_registration_number VARCHAR(100) UNIQUE,
            owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            head_office_address TEXT,
            contact_email VARCHAR(255),
            contact_phone VARCHAR(30),
            verification_status VARCHAR(30) DEFAULT 'APPROVED' NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_companies_business_name ON pharmacy_companies(business_name)")

    # ── 2. Add company_id to pharmacies ───────────────────────────────────────
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'pharmacies' AND column_name = 'company_id'
            ) THEN
                ALTER TABLE pharmacies ADD COLUMN company_id UUID REFERENCES pharmacy_companies(id) ON DELETE SET NULL;
                CREATE INDEX IF NOT EXISTS idx_pharmacies_company_id ON pharmacies(company_id);
            END IF;
        END $$;
    """)

    # ── 3. Drop pharmacies.registration_number unique constraint if present ───
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'pharmacies_registration_number_key'
            ) THEN
                ALTER TABLE pharmacies DROP CONSTRAINT pharmacies_registration_number_key;
            END IF;
        END $$;
    """)

    # ── 4. Create pharmacist_profiles table ───────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS pharmacist_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            slmc_number VARCHAR(50) NOT NULL UNIQUE,
            registration_status VARCHAR(30) DEFAULT 'ACTIVE' NOT NULL,
            verification_status VARCHAR(30) DEFAULT 'VERIFIED' NOT NULL,
            verified_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_pharmacist_slmc ON pharmacist_profiles(slmc_number)")

    # ── 5. Create branch_pharmacist_assignments table ─────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS branch_pharmacist_assignments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            pharmacy_id UUID NOT NULL REFERENCES pharmacies(id) ON DELETE CASCADE,
            pharmacist_id UUID NOT NULL REFERENCES pharmacist_profiles(id) ON DELETE CASCADE,
            appointment_type VARCHAR(50) DEFAULT 'RESPONSIBLE_PHARMACIST' NOT NULL,
            start_date DATE DEFAULT CURRENT_DATE NOT NULL,
            end_date DATE,
            status VARCHAR(30) DEFAULT 'ACTIVE' NOT NULL,
            supporting_document_id UUID REFERENCES pharmacy_compliance_documents(id) ON DELETE SET NULL,
            nmra_acknowledgement VARCHAR(100),
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_assignments_pharmacy ON branch_pharmacist_assignments(pharmacy_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_assignments_pharmacist ON branch_pharmacist_assignments(pharmacist_id)")

    # ── 6. Create pharmacy_licenses table ─────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS pharmacy_licenses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            pharmacy_id UUID NOT NULL REFERENCES pharmacies(id) ON DELETE CASCADE,
            licence_number VARCHAR(100) NOT NULL,
            issued_date DATE,
            expiry_date DATE,
            document_id UUID REFERENCES pharmacy_compliance_documents(id) ON DELETE SET NULL,
            verification_status VARCHAR(30) DEFAULT 'VERIFIED' NOT NULL,
            verified_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            verified_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_licenses_pharmacy_id ON pharmacy_licenses(pharmacy_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_licenses_licence_number ON pharmacy_licenses(licence_number)")

    # ── 7. Relax pharmacy_staff_profiles user_id constraint to (user_id, pharmacy_id) ──
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'pharmacy_staff_profiles_user_id_key'
            ) THEN
                ALTER TABLE pharmacy_staff_profiles DROP CONSTRAINT pharmacy_staff_profiles_user_id_key;
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_staff_user_pharmacy'
            ) THEN
                ALTER TABLE pharmacy_staff_profiles ADD CONSTRAINT uq_staff_user_pharmacy UNIQUE (user_id, pharmacy_id);
            END IF;
        END $$;
    """)

    # ── 8. Add snapshots to pharmacy_audit_log ────────────────────────────────
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'pharmacy_audit_log' AND column_name = 'actor_name_snapshot'
            ) THEN
                ALTER TABLE pharmacy_audit_log ADD COLUMN actor_name_snapshot VARCHAR(255);
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'pharmacy_audit_log' AND column_name = 'actor_role_snapshot'
            ) THEN
                ALTER TABLE pharmacy_audit_log ADD COLUMN actor_role_snapshot VARCHAR(60);
            END IF;
        END $$;
    """)

    # ── 9. IDEMPOTENT DATA BACKFILL ───────────────────────────────────────────
    # 9a. Create Companies for known networks and link pharmacies
    op.execute("""
        DO $$
        DECLARE
            hg_id UUID := gen_random_uuid();
            uc_id UUID := gen_random_uuid();
            cg_id UUID := gen_random_uuid();
            os_id UUID := gen_random_uuid();
            cp_id UUID := gen_random_uuid();
            hx_id UUID := gen_random_uuid();
            r RECORD;
            comp_id UUID;
        BEGIN
            -- 1. Healthguard Pharmacies (Pvt) Ltd
            IF NOT EXISTS (SELECT 1 FROM pharmacy_companies WHERE business_name ILIKE '%Healthguard%') THEN
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (hg_id, 'Healthguard Pharmacies (Pvt) Ltd', 'PV-00456', 'No. 125, Station Road, Colombo 03', '+94112345678', 'APPROVED');
                UPDATE pharmacies SET company_id = hg_id WHERE name ILIKE '%Healthguard%' AND company_id IS NULL;
            ELSE
                SELECT id INTO hg_id FROM pharmacy_companies WHERE business_name ILIKE '%Healthguard%' LIMIT 1;
                UPDATE pharmacies SET company_id = hg_id WHERE name ILIKE '%Healthguard%' AND company_id IS NULL;
            END IF;

            -- 2. Union Chemists (Pvt) Ltd
            IF NOT EXISTS (SELECT 1 FROM pharmacy_companies WHERE business_name ILIKE '%Union Chemists%') THEN
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (uc_id, 'Union Chemists (Pvt) Ltd', 'PV-00123', 'No. 460, Union Place, Colombo 02', '+94112698765', 'APPROVED');
                UPDATE pharmacies SET company_id = uc_id WHERE name ILIKE '%Union Chemists%' AND company_id IS NULL;
            ELSE
                SELECT id INTO uc_id FROM pharmacy_companies WHERE business_name ILIKE '%Union Chemists%' LIMIT 1;
                UPDATE pharmacies SET company_id = uc_id WHERE name ILIKE '%Union Chemists%' AND company_id IS NULL;
            END IF;

            -- 3. Cargills Foods Company (Pvt) Ltd
            IF NOT EXISTS (SELECT 1 FROM pharmacy_companies WHERE business_name ILIKE '%Cargills%') THEN
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (cg_id, 'Cargills Foods Company (Pvt) Ltd - Pharmacy Division', 'PV-00910', 'No. 40, York Street, Colombo 01', '+94112427777', 'APPROVED');
                UPDATE pharmacies SET company_id = cg_id WHERE name ILIKE '%Cargills%' AND company_id IS NULL;
            ELSE
                SELECT id INTO cg_id FROM pharmacy_companies WHERE business_name ILIKE '%Cargills%' LIMIT 1;
                UPDATE pharmacies SET company_id = cg_id WHERE name ILIKE '%Cargills%' AND company_id IS NULL;
            END IF;

            -- 4. State Pharmaceuticals Corporation (Rajya Osu Sala)
            IF NOT EXISTS (SELECT 1 FROM pharmacy_companies WHERE business_name ILIKE '%Rajya Osu Sala%') THEN
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (os_id, 'State Pharmaceuticals Corporation - Rajya Osu Sala', 'GA-00088', 'No. 75, Sir Baron Jayathilake Mawatha, Colombo 01', '+94112320356', 'APPROVED');
                UPDATE pharmacies SET company_id = os_id WHERE name ILIKE '%Rajya Osu Sala%' AND company_id IS NULL;
            ELSE
                SELECT id INTO os_id FROM pharmacy_companies WHERE business_name ILIKE '%Rajya Osu Sala%' LIMIT 1;
                UPDATE pharmacies SET company_id = os_id WHERE name ILIKE '%Rajya Osu Sala%' AND company_id IS NULL;
            END IF;

            -- 5. City Pharmacy (Pvt) Ltd
            IF NOT EXISTS (SELECT 1 FROM pharmacy_companies WHERE business_name ILIKE '%City Pharmacy%') THEN
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (cp_id, 'City Pharmacy (Pvt) Ltd', 'PV-00789', 'Galle Road, Dehiwala', '+94112713344', 'APPROVED');
                UPDATE pharmacies SET company_id = cp_id WHERE name ILIKE '%City Pharmacy%' AND company_id IS NULL;
            ELSE
                SELECT id INTO cp_id FROM pharmacy_companies WHERE business_name ILIKE '%City Pharmacy%' LIMIT 1;
                UPDATE pharmacies SET company_id = cp_id WHERE name ILIKE '%City Pharmacy%' AND company_id IS NULL;
            END IF;

            -- 6. HealthX Dispensary
            IF NOT EXISTS (SELECT 1 FROM pharmacy_companies WHERE business_name ILIKE '%HealthX%') THEN
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (hx_id, 'HealthX Healthcare Dispensary', 'NMRA-PH-2343', 'Nugegoda, Sri Lanka', '+94770000001', 'APPROVED');
                UPDATE pharmacies SET company_id = hx_id WHERE name ILIKE '%HealthX%' AND company_id IS NULL;
            ELSE
                SELECT id INTO hx_id FROM pharmacy_companies WHERE business_name ILIKE '%HealthX%' LIMIT 1;
                UPDATE pharmacies SET company_id = hx_id WHERE name ILIKE '%HealthX%' AND company_id IS NULL;
            END IF;

            -- 7. Any remaining unassigned pharmacies get their own company
            FOR r IN SELECT id, name, registration_number, phone_number, address FROM pharmacies WHERE company_id IS NULL LOOP
                comp_id := gen_random_uuid();
                INSERT INTO pharmacy_companies (id, business_name, business_registration_number, head_office_address, contact_phone, verification_status)
                VALUES (comp_id, r.name || ' (Pvt) Ltd', r.registration_number, r.address, r.phone_number, 'APPROVED')
                ON CONFLICT (business_registration_number) DO NOTHING;

                UPDATE pharmacies SET company_id = comp_id WHERE id = r.id AND company_id IS NULL;
            END LOOP;
        END $$;
    """)

    # 9b. Backfill pharmacist_profiles from pharmacy_staff_profiles
    op.execute("""
        INSERT INTO pharmacist_profiles (id, user_id, slmc_number, registration_status, verification_status, verified_at, created_at, updated_at)
        SELECT DISTINCT ON (user_id)
            gen_random_uuid(),
            user_id,
            slmc_number,
            'ACTIVE',
            'VERIFIED',
            NOW(),
            NOW(),
            NOW()
        FROM pharmacy_staff_profiles
        WHERE slmc_number IS NOT NULL AND slmc_number != ''
        ON CONFLICT (user_id) DO NOTHING
    """)

    # 9c. Backfill branch_pharmacist_assignments for existing custody pharmacists
    op.execute("""
        INSERT INTO branch_pharmacist_assignments (id, pharmacy_id, pharmacist_id, appointment_type, start_date, status, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            s.pharmacy_id,
            p.id,
            'RESPONSIBLE_PHARMACIST',
            CURRENT_DATE,
            'ACTIVE',
            NOW(),
            NOW()
        FROM pharmacy_staff_profiles s
        JOIN pharmacist_profiles p ON p.user_id = s.user_id
        WHERE s.staff_role IN ('Owner / Chief Pharmacist', 'Designated Manager / Pharmacist')
          AND s.is_active = true
        ON CONFLICT DO NOTHING
    """)

    # 9d. Backfill pharmacy_licenses from pharmacies.nmra_license
    op.execute("""
        INSERT INTO pharmacy_licenses (id, pharmacy_id, licence_number, verification_status, created_at)
        SELECT
            gen_random_uuid(),
            id,
            COALESCE(nmra_license, registration_number),
            'VERIFIED',
            NOW()
        FROM pharmacies
        WHERE nmra_license IS NOT NULL OR registration_number IS NOT NULL
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    pass

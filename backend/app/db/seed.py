"""Idempotent seed script: roles, complaint categories (from every module's
module.json), a default escalation rule, and a SUPER_ADMIN account for first
login. Run with:  python -m app.db.seed
"""
import asyncio
import json
import logging

from sqlalchemy import select

from app.core.module_loader import discover_modules
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.complaint import ComplaintCategory
from app.models.enums import RoleName
from app.models.escalation import EscalationRule
from app.models.module_registry import ModuleRegistryEntry
from app.models.user import Role, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

CATEGORY_METADATA = {
    "ROAD_DAMAGE": ("Road Damage", "MEDIUM", "road"),
    "STREETLIGHT_PROBLEM": ("Streetlight Problem", "LOW", "lightbulb"),
    "PUBLIC_TOILET_ISSUE": ("Public Toilet Issue", "MEDIUM", "toilet"),
    "OTHER": ("Other Civic Issue", "LOW", "help-circle"),
    "DRAIN_BLOCKAGE": ("Drain Blockage", "HIGH", "droplet"),
    "WATER_STAGNATION": ("Water Stagnation", "HIGH", "droplet"),
    "GARBAGE_DUMPING": ("Garbage Dumping", "MEDIUM", "trash"),
    "ILLEGAL_DUMPING": ("Illegal Dumping", "HIGH", "trash-2"),
    "PLASTIC_WASTE": ("Plastic Waste", "MEDIUM", "package"),
    "LAKE_POLLUTION": ("Lake Pollution", "HIGH", "waves"),
    "RIVER_POLLUTION": ("River Pollution", "CRITICAL", "waves"),
    "CANAL_BLOCKAGE": ("Canal Blockage", "HIGH", "waves"),
    "WATER_BODY_ENCROACHMENT": ("Water Body Encroachment", "HIGH", "alert-triangle"),
    "REDUCED_WATER_LEVEL": ("Reduced Water Level", "MEDIUM", "trending-down"),
    "FALLEN_TREE": ("Fallen Tree", "MEDIUM", "tree-deciduous"),
    "CROP_DISEASE": ("Crop Disease", "MEDIUM", "leaf"),
    "CROP_PEST": ("Crop Pest", "MEDIUM", "bug"),
    "WILDLIFE_SIGHTING": ("Wildlife Sighting", "LOW", "paw-print"),
    "HABITAT_DAMAGE": ("Habitat Damage", "HIGH", "alert-triangle"),
    "FLOOD_REPORT": ("Flood Report", "CRITICAL", "cloud-rain"),
    "DISASTER_DAMAGE": ("Disaster Damage", "CRITICAL", "alert-octagon"),
}


async def seed_roles(db) -> None:
    existing = {r.name for r in (await db.execute(select(Role))).scalars().all()}
    for role_name in RoleName:
        if role_name.value not in existing:
            db.add(Role(name=role_name.value, description=f"{role_name.value.title()} role"))
    await db.commit()


async def seed_categories_and_registry(db) -> None:
    existing_categories = {c.code for c in (await db.execute(select(ComplaintCategory))).scalars().all()}
    existing_modules = {m.module_id for m in (await db.execute(select(ModuleRegistryEntry))).scalars().all()}

    for manifest in discover_modules():
        if manifest.module_id not in existing_modules:
            db.add(
                ModuleRegistryEntry(
                    module_id=manifest.module_id,
                    name=manifest.name,
                    version=manifest.version,
                    description=manifest.description,
                    api_version=manifest.api_version,
                    author=manifest.author,
                    enabled=True,
                    manifest=manifest.raw,
                )
            )
        for code in manifest.raw.get("categories", []):
            if code in existing_categories:
                continue
            name, severity, icon = CATEGORY_METADATA.get(code, (code.replace("_", " ").title(), "MEDIUM", "alert-circle"))
            db.add(
                ComplaintCategory(
                    code=code,
                    name=name,
                    module_id=manifest.module_id,
                    default_severity=severity,
                    icon=icon,
                )
            )
            existing_categories.add(code)
    await db.commit()


async def seed_default_escalation_rule(db) -> None:
    default_rule = (await db.execute(select(EscalationRule).where(EscalationRule.category_code.is_(None)))).scalar_one_or_none()
    if default_rule is None:
        db.add(EscalationRule(category_code=None, deadline_days=3, initial_authority_level="LOCAL_BODY", escalation_level_1="BLOCK_LEVEL", escalation_level_2="DISTRICT_LEVEL", reminder_before_days=1))
    # A tighter deadline for disaster-grade urgency.
    disaster_rule = (await db.execute(select(EscalationRule).where(EscalationRule.category_code == "FLOOD_REPORT"))).scalar_one_or_none()
    if disaster_rule is None:
        db.add(EscalationRule(category_code="FLOOD_REPORT", deadline_days=1, initial_authority_level="BLOCK_LEVEL", escalation_level_1="DISTRICT_LEVEL", escalation_level_2="DISTRICT_LEVEL", reminder_before_days=0))
    await db.commit()


async def seed_super_admin(db) -> None:
    email = "admin@nellaigreencivic.org"
    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing:
        return
    super_admin_role = (await db.execute(select(Role).where(Role.name == RoleName.SUPER_ADMIN.value))).scalar_one_or_none()
    admin_role = (await db.execute(select(Role).where(Role.name == RoleName.ADMIN.value))).scalar_one_or_none()
    user = User(
        full_name="Platform Administrator",
        email=email,
        password_hash=hash_password("ChangeMe123!"),
        is_active=True,
        is_verified=True,
        roles=[r for r in [super_admin_role, admin_role] if r],
    )
    db.add(user)
    await db.commit()
    logger.warning("Seeded SUPER_ADMIN %s with password 'ChangeMe123!' -- change this immediately.", email)


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_roles(db)
        await seed_categories_and_registry(db)
        await seed_default_escalation_rule(db)
        await seed_super_admin(db)
    logger.info("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())

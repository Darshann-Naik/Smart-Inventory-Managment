# /scripts/init_db.py
import asyncio
import sys
import os
import typer
import logging
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# --- Setup Project Path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


# --- Explicit Model Imports ---
from app.user_service import models as user_models
from app.store_service import models as store_models
from app.category_service import models as category_models
from app.product_service import models as product_models
from app.transaction_service import models as transaction_models
from app.store_product_service import models as store_product_models

# --- Core Imports ---
from core.database import create_db_and_tables, drop_db_and_tables, AsyncSessionFactory
from core.security import hash_password

# --- Typer CLI Application ---
cli = typer.Typer()


async def seed_roles(db: AsyncSession):
    """Seeds the default roles into the database if they don't exist."""
    log.info("Seeding default roles...")
    roles_to_create = {
        "admin": "Administrator with store-level permissions.",
        "super_admin": "Super Administrator with all permissions.",
        "employee": "An employee of a retail shop.",
    }
    
    for role_name, role_desc in roles_to_create.items():
        statement = select(user_models.Role).where(user_models.Role.name == role_name)
        result = await db.execute(statement)
        if not result.scalar_one_or_none():
            role = user_models.Role(name=role_name, description=role_desc)
            db.add(role)
            log.info(f"Created role: {role_name}")
            
    await db.commit()
    log.info("Role seeding complete.")


async def seed_default_user_and_store(db: AsyncSession):
    """
    Creates a default super admin user and an associated default store.
    """
    log.info("Seeding default user and store...")
    admin_email = "admin@example.com"
    store_name = "Default Store"

    # 1. Check if the user already exists
    user_stmt = select(user_models.User).where(user_models.User.email == admin_email)
    existing_user = (await db.execute(user_stmt)).scalar_one_or_none()
    if existing_user:
        log.info(f"User '{admin_email}' already exists. Skipping seeding.")
        return

    # 2. Get the super_admin role
    role_stmt = select(user_models.Role).where(user_models.Role.name == "super_admin")
    super_admin_role = (await db.execute(role_stmt)).scalar_one_or_none()
    if not super_admin_role:
        log.error("Super admin role not found. Please ensure roles are seeded first.")
        return

    # 3. Create both User and Store objects in memory
    default_store = store_models.Store(
        name=store_name,
        gstin="DEFAULTGSTIN001",
        is_active=True,
    )
    
    admin_user = user_models.User(
        user_id="SUSA001",
        email=admin_email,
        hashed_password=hash_password("test@123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        role=super_admin_role, # Assign the single role
        store_id=default_store.id,
    )
    
    default_store.created_by = admin_user.id

    # 5. Add both to the session and commit
    db.add(admin_user)
    db.add(default_store)
    await db.commit()

    await db.refresh(admin_user)
    await db.refresh(default_store)

    log.info(f"Created default user: {admin_user.email} with ID: {admin_user.id}")
    log.info(f"Created default store: {default_store.name} with ID: {default_store.id}")
    log.info(f"Linked user {admin_user.email} to store {default_store.name}.")


async def run_init_db():
    """The main asynchronous function that orchestrates the database setup."""
    log.info("--- Starting Database Initialization ---")
    
    log.info("Dropping all tables...")
    await drop_db_and_tables()
    
    log.info("Creating all tables...")
    await create_db_and_tables()
    
    log.info("Seeding initial data...")
    async with AsyncSessionFactory() as session:
        await seed_roles(session)
        await seed_default_user_and_store(session)
    
    log.info("--- Database Initialization Complete ---")


@cli.command()
def main():
    """
    Main entry point for the CLI. Drops, creates, and seeds the database.
    """
    print("--- WARNING: This will drop all existing data. ---")
    
    asyncio.run(run_init_db())
    
    print("--- Database reset and seeding complete. ---")


if __name__ == "__main__":
    cli()
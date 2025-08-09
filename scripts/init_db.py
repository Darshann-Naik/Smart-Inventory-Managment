# /scripts/init_db.py
import asyncio
import sys
import os
import typer
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

# --- THIS IS THE CRITICAL AND ROBUST FIX ---
# Add the project's root directory (the parent of 'scripts') to the Python path.
# This ensures that Python can find the 'app' and 'core' packages correctly,
# regardless of how the script is run.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
# -------------------------------------------

# --- CORRECTED IMPORTS ---
# Import each model file explicitly to ensure SQLAlchemy's metadata is populated
# before any database operations are called. This prevents UnmappedClassError.
from app.user_service import models as user_models
from app.store_service import models as store_models
from app.category_service import models as category_models
from app.product_service import models as product_models
from app.transaction_service import models as transaction_models
from app.store_product_service import models as store_product_models
# -------------------------

from core.database import create_db_and_tables, drop_db_and_tables, AsyncSessionFactory

cli = typer.Typer()

async def seed_roles(db: AsyncSession):
    """Checks for and creates roles if they don't exist."""
    roles_to_create = {
        "super_admin": "Super Administrator with all permissions.",
        "shop_owner": "Owner of a retail shop.",
        "employee": "An employee of a retail shop.",
    }
    for role_name, role_desc in roles_to_create.items():
        # Use the specific user_models import
        statement = select(user_models.Role).where(user_models.Role.name == role_name)
        result = await db.execute(statement)
        if not result.scalar_one_or_none():
            role = user_models.Role(name=role_name, description=role_desc)
            db.add(role)
            print(f"Created role: {role_name}")
    await db.commit()

@cli.command()
def main():
    """
    Drops all tables, re-initializes the database, and seeds default data.
    """
    print("--- WARNING: This will drop all existing data. ---")

    async def init_db():
        print("Dropping all tables...")
        await drop_db_and_tables()
        print("Creating all tables...")
        await create_db_and_tables()
        print("Seeding initial data...")
        async with AsyncSessionFactory() as session:
            await seed_roles(session)

    asyncio.run(init_db())
    print("--- Database reset and seeding complete. ---")

if __name__ == "__main__":
    cli()

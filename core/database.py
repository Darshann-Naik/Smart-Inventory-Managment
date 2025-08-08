# /core/database.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.config import settings

# Create the async engine
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

# Async session factory
AsyncSessionFactory = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session.
    Ensures the session is closed after the request is finished.
    """
    async with AsyncSessionFactory() as session:
        yield session

# --- Add this new function ---
async def drop_db_and_tables():
    """
    Drops all tables from the database. USE WITH CAUTION.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
# -----------------------------

async def create_db_and_tables():
    """
    Initialize the database and create tables.
    Should be called once on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
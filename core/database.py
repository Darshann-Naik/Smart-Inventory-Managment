from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text

from core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

AsyncSessionFactory = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session

async def drop_db_and_tables():
    """
    Drops all tables in dependency order with CASCADE to avoid FK constraint errors.
    USE WITH CAUTION.
    """
    async with engine.begin() as conn:
        # Drop tables in order of dependency - children first, then parents.
        # Replace table names with your actual table names as needed.
        await conn.execute(text("DROP TABLE IF EXISTS storeproduct CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS transaction CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS product CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS category CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS store CASCADE"))
        await conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        await conn.execute(text("DROP TABLE IF EXISTS role CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS userrolelink CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS sequencetracker CASCADE"))
        # Add any other tables you have

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

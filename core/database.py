# /core/database.py
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
    """
    Provides a transactionally-scoped database session per request.
    """
    async with AsyncSessionFactory() as session:
        async with session.begin(): # This starts the transaction
            try:
                yield session
                # If no exception, the context manager will commit automatically.
            except:
                # If an exception occurs, the context manager will roll back.
                await session.rollback()
                raise

async def drop_db_and_tables():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS storeproduct CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS inventorytransaction CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS product CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS category CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS store CASCADE"))
        await conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        await conn.execute(text("DROP TABLE IF EXISTS role CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS userrolelink CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS sequencetracker CASCADE"))
        await conn.execute(text("TRUNCATE TABLE audit_logs RESTART IDENTITY CASCADE"))
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
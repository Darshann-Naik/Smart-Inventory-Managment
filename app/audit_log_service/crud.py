# /app/audit_log_service/crud.py
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from . import models, schemas


async def create_audit_log(db: AsyncSession, log_entry: schemas.AuditLogCreate) -> models.AuditLog:
    """Creates a new audit log entry in the database."""
    db_log = models.AuditLog.model_validate(log_entry)
    db.add(db_log)
    await db.flush()
    return db_log


async def get_audit_logs(db: AsyncSession, filters: schemas.AuditLogFilterParams) -> List[models.AuditLog]:
    """Retrieves a paginated and filtered list of audit logs."""
    statement = select(models.AuditLog)

    if filters.start_ts:
        statement = statement.where(models.AuditLog.created_at >= filters.start_ts)
    if filters.end_ts:
        statement = statement.where(models.AuditLog.created_at <= filters.end_ts)
    if filters.user_id:
        statement = statement.where(models.AuditLog.user_id == filters.user_id)
    if filters.entity_type:
        statement = statement.where(models.AuditLog.entity_type == filters.entity_type)
    if filters.entity_id:
        statement = statement.where(models.AuditLog.entity_id == filters.entity_id)
    if filters.action:
        statement = statement.where(models.AuditLog.action == filters.action)
    if filters.store_id:
        statement = statement.where(models.AuditLog.store_id == filters.store_id)

    statement = statement.order_by(getattr(models.AuditLog, filters.sort).desc())
    statement = statement.offset(filters.offset).limit(filters.limit)

    result = await db.execute(statement)
    return result.scalars().all()


async def get_audit_log_by_id(db: AsyncSession, log_id: uuid.UUID) -> Optional[models.AuditLog]:
    """Retrieves a single audit log by its ID."""
    return await db.get(models.AuditLog, log_id)


async def delete_logs_before(db: AsyncSession, cutoff_date: datetime) -> int:
    """Deletes audit logs older than a specified cutoff date."""
    statement = delete(models.AuditLog).where(models.AuditLog.created_at < cutoff_date)
    result = await db.execute(statement)
    return result.rowcount
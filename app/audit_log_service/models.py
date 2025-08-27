# /app/audit_log_service/models.py
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    """
    Represents an immutable audit log entry.
    """
    __tablename__ = "audit_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", nullable=True, index=True)
    store_id: Optional[uuid.UUID] = Field(default=None, foreign_key="store.id", nullable=True, index=True)

    action: str = Field(index=True)
    entity_type: Optional[str] = Field(default=None, index=True)
    entity_id: Optional[str] = Field(default=None, index=True)

    before: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    after: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    changes: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))

    request_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    raw: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))

    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )
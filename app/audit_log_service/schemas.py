# /app/audit_log_service/schemas.py
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    user_id: Optional[uuid.UUID] = None
    store_id: Optional[uuid.UUID] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    request_metadata: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogOut(AuditLogBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogFilterParams(BaseModel):
    start_ts: Optional[datetime] = None
    end_ts: Optional[datetime] = None
    user_id: Optional[uuid.UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action: Optional[str] = None
    store_id: Optional[uuid.UUID] = None
    q: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    sort: str = Field("created_at", enum=["created_at", "action", "entity_type"])
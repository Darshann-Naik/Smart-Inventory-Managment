# /app/audit_log_service/services.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from . import crud, schemas
from app.user_service.models import User # Import the User model for type hinting

logger = logging.getLogger(__name__)


def _mask_sensitive_fields(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively masks sensitive fields in a dictionary."""
    if not data:
        return None
    
    clean_data = {}
    for key, value in data.items():
        if key in settings.AUDIT_PII_FIELDS:
            clean_data[key] = f"<REDACTED:{key}>"
        elif isinstance(value, dict):
            clean_data[key] = _mask_sensitive_fields(value)
        elif isinstance(value, list):
            clean_data[key] = [_mask_sensitive_fields(item) if isinstance(item, dict) else item for item in value]
        else:
            clean_data[key] = value
    return clean_data

def _calculate_changes(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates the difference between two dictionaries, representing the state
    of an object before and after a change.
    """
    changes = {}
    all_keys = before.keys() | after.keys()
    
    for key in all_keys:
        before_value = before.get(key)
        after_value = after.get(key)
        
        if before_value != after_value:
            changes[key] = {
                "before": before_value,
                "after": after_value
            }
            
    return changes


class AuditLogger:
    def __init__(self, db: AsyncSession, current_user: Optional[User] = None, request: Optional[Request] = None):
        self.db = db
        self.request = request
        self.current_user = current_user

    async def record_event(
        self,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Creates and stores a detailed audit log event."""
        log_metadata = {}
        if self.request:
            log_metadata = {
                "ip": self.request.client.host,
                "user_agent": self.request.headers.get("user-agent"),
            }
        else:
            log_metadata = {"source": "system"}

        if metadata:
            log_metadata.update(metadata)
        
        user_id = self.current_user.id if self.current_user else None
        store_id = self.current_user.store_id if self.current_user and hasattr(self.current_user, 'store_id') else None
            
        if before and after and changes is None:
            changes = _calculate_changes(before, after)

        log_entry = schemas.AuditLogCreate(
            user_id=user_id,
            store_id=store_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=_mask_sensitive_fields(before),
            after=_mask_sensitive_fields(after),
            changes=_mask_sensitive_fields(changes),
            metadata=log_metadata,
        )
        
        try:
            await crud.create_audit_log(self.db, log_entry)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}", exc_info=True)



async def cleanup_old_audit_logs(db: AsyncSession):
    """Deletes audit logs older than the configured retention period."""
    if settings.AUDIT_RETENTION_DAYS > 0:
        cutoff_date = datetime.utcnow() - timedelta(days=settings.AUDIT_RETENTION_DAYS)
        deleted_count = await crud.delete_logs_before(db, cutoff_date)
        logger.info(f"Audit log cleanup: Deleted {deleted_count} logs older than {cutoff_date}.")
        return {"deleted_count": deleted_count}
    return {"message": "Audit log retention is disabled."}
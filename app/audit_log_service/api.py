# /app/audit_log_service/api.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from app.user_service.dependencies import require_role
from . import schemas, services, crud

router = APIRouter()

@router.get(
    "",
    response_model=List[schemas.AuditLogOut],
    summary="Search and filter audit logs",
    dependencies=[Depends(require_role(["super_admin", "admin"]))],
)
async def search_audit_logs(
    db: AsyncSession = Depends(get_db_session),
    filters: schemas.AuditLogFilterParams = Depends(),
):
    """
    Retrieves a list of audit logs based on filter criteria.
    Requires `admin` or `super_admin` role.
    """
    return await crud.get_audit_logs(db, filters)


@router.get(
    "/{log_id}",
    response_model=schemas.AuditLogOut,
    summary="Get a specific audit log by ID",
    dependencies=[Depends(require_role(["super_admin", "admin"]))],
)
async def get_audit_log(log_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieves a single audit log by its unique ID.
    Requires `admin` or `super_admin` role.
    """
    log = await crud.get_audit_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    return log


@router.post(
    "/cleanup",
    summary="Trigger audit log cleanup job",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def trigger_cleanup(db: AsyncSession = Depends(get_db_session)):
    """
    Manually triggers the job to delete old audit logs based on the retention policy.
    Requires `super_admin` role.
    """
    # In a production system, this would likely be a background task.
    # For this example, we'll run it synchronously.
    result = await services.cleanup_old_audit_logs(db)
    return {"message": "Audit log cleanup job triggered.", "details": result}
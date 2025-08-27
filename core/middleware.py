# /core/middleware.py
import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.audit_log_service.services import AuditLogger
from app.user_service.dependencies import get_current_user
from core.database import AsyncSessionFactory

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Attach a unique ID to the request for tracing
        request.state.request_id = str(uuid.uuid4())
        
        # Create a single session and transaction that will be used for the entire request
        async with AsyncSessionFactory() as session:
            request.state.db = session
            try:
                # Attempt to get user, but don't fail if not authenticated
                token = request.headers.get("authorization")
                if token and token.startswith("Bearer "):
                    try:
                        request.state.user = await get_current_user(db=session, token=token.replace("Bearer ", ""))
                    except Exception:
                        request.state.user = None
                else:
                    request.state.user = None

                start_time = time.time()
                
                # Process the request within a single transaction
                async with session.begin():
                    response = await call_next(request)
                
                process_time = (time.time() - start_time) * 1000

                # Record the high-level API request event using the same session
                audit_logger = AuditLogger(db=session, request=request)
                await audit_logger.record_event(
                    action="api.request",
                    metadata={
                        "method": request.method,
                        "path": request.url.path,
                        "query_params": str(request.query_params),
                        "status_code": response.status_code,
                        "process_time_ms": f"{process_time:.2f}",
                    },
                )
                await session.commit() # Commit the audit log entry

            except Exception as e:
                # If any exception occurs during the request, roll back the transaction
                await session.rollback()
                raise e

        return response
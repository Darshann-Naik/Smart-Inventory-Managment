# /core/exceptions.py
from fastapi import HTTPException, status

class APIException(HTTPException):
    """Base exception for this application."""
    def __init__(self, status_code: int, title: str, detail: str):
        self.title = title
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(APIException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource Not Found",
            detail=f"The requested resource '{resource}' with ID '{resource_id}' was not found."
        )

class UnauthenticatedException(APIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Authentication Failed",
            detail="Incorrect username or password.",
        )

class UnauthorizedException(APIException):
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission Denied",
            detail=detail,
        )

class ConflictException(APIException):
     def __init__(self, detail: str):
         super().__init__(
             status_code=status.HTTP_409_CONFLICT,
             title="Conflict",
             detail=detail
         )

class BadRequestException(APIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=detail
        )

class InvalidTokenException(APIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Invalid Token",
            detail="Could not validate credentials. The token may be expired or invalid.",
        )
# /app/store_service/schemas.py
import uuid
from typing import Optional
from pydantic import BaseModel

class StoreBase(BaseModel):
    name: str
    gstin: Optional[str] = None

class StoreCreate(StoreBase):
    pass

class StoreRead(StoreBase):
    id: uuid.UUID
    
class StoreUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
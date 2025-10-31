from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class ProcessOperationBase(BaseModel):
    code: str
    name_en: str
    name_ru: str
    icon: Optional[str] = None
    resource_url: Optional[str] = None
    availability_condition: Optional[str] = None
    cancel: bool = False
    move_to_state_script: Optional[str] = None
    workflow: Optional[str] = None
    database: Optional[str] = None


class ProcessOperationCreate(ProcessOperationBase):
    type_id: UUID
    available_state_ids: Optional[List[UUID]] = []


class ProcessOperationUpdate(ProcessOperationBase):
    type_id: Optional[UUID] = None
    available_state_ids: Optional[List[UUID]] = None


class ProcessOperationSchema(ProcessOperationBase):
    id: UUID
    type_id: UUID
    available_state_ids: Optional[List[UUID]] = []
    
    class Config:
        from_attributes = True


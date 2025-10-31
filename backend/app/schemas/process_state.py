from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ProcessStateBase(BaseModel):
    code: str
    name_en: str
    name_ru: str
    color_code: Optional[str] = None
    allow_edit: bool = False
    allow_delete: bool = False
    start: bool = False
    operation_list_script: Optional[str] = None


class ProcessStateCreate(ProcessStateBase):
    type_id: UUID


class ProcessStateUpdate(ProcessStateBase):
    type_id: Optional[UUID] = None


class ProcessStateSchema(ProcessStateBase):
    id: UUID
    type_id: UUID
    
    class Config:
        from_attributes = True


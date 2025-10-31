from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ProcessTypeBase(BaseModel):
    code: str
    name_en: str
    name_ru: str
    attributes_table: Optional[str] = None
    parent_id: Optional[UUID] = None


class ProcessTypeCreate(ProcessTypeBase):
    pass


class ProcessTypeSchema(ProcessTypeBase):
    id: UUID
    
    class Config:
        from_attributes = True


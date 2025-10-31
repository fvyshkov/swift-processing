from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from .process_type import ProcessTypeCreate
from .process_state import ProcessStateCreate, ProcessStateUpdate
from .process_operation import ProcessOperationCreate, ProcessOperationUpdate


class StateChanges(BaseModel):
    created: List[ProcessStateCreate] = []
    updated: List[ProcessStateUpdate] = []
    deleted: List[UUID] = []


class OperationChanges(BaseModel):
    created: List[ProcessOperationCreate] = []
    updated: List[ProcessOperationUpdate] = []
    deleted: List[UUID] = []


class SaveAllRequest(BaseModel):
    type: Optional[ProcessTypeCreate] = None
    states: Optional[StateChanges] = None
    operations: Optional[OperationChanges] = None
    operation_states: Optional[Dict[str, List[UUID]]] = {}


class SaveAllResponse(BaseModel):
    success: bool
    message: str


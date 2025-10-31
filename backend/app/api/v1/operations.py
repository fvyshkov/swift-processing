from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_db
from app.schemas.process_operation import ProcessOperationSchema, ProcessOperationCreate, ProcessOperationUpdate
from app.crud import process_operation, process_type

router = APIRouter()


@router.get("/types/{type_code}/operations", response_model=List[ProcessOperationSchema])
async def get_operations_for_type(type_code: str, db: AsyncSession = Depends(get_db)):
    """Get all operations for a type"""
    db_type = await process_type.get_by_code(db, type_code)
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    
    operations = await process_operation.get_by_type_id(db, db_type.id)
    
    # Add available_state_ids to response
    result = []
    for op in operations:
        op_dict = {
            "id": op.id,
            "type_id": op.type_id,
            "code": op.code,
            "name_en": op.name_en,
            "name_ru": op.name_ru,
            "icon": op.icon,
            "resource_url": op.resource_url,
            "availability_condition": op.availability_condition,
            "cancel": op.cancel,
            "move_to_state_script": op.move_to_state_script,
            "workflow": op.workflow,
            "database": op.database,
            "available_state_ids": [state.id for state in op.available_states]
        }
        result.append(op_dict)
    
    return result


@router.get("/operations/{operation_id}", response_model=ProcessOperationSchema)
async def get_operation(operation_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get single operation"""
    operation = await process_operation.get_by_id(db, operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return {
        **operation.__dict__,
        "available_state_ids": [state.id for state in operation.available_states]
    }


@router.post("/types/{type_code}/operations", response_model=ProcessOperationSchema)
async def create_operation(type_code: str, operation_data: ProcessOperationCreate, db: AsyncSession = Depends(get_db)):
    """Create new operation"""
    db_type = await process_type.get_by_code(db, type_code)
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    
    op = await process_operation.create(db, operation_data)
    return {
        **op.__dict__,
        "available_state_ids": [state.id for state in op.available_states]
    }


@router.put("/operations/{operation_id}", response_model=ProcessOperationSchema)
async def update_operation(operation_id: UUID, operation_data: ProcessOperationUpdate, db: AsyncSession = Depends(get_db)):
    """Update operation"""
    op = await process_operation.update(db, operation_id, operation_data)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return {
        **op.__dict__,
        "available_state_ids": [state.id for state in op.available_states]
    }


@router.delete("/operations/{operation_id}")
async def delete_operation(operation_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete operation"""
    await process_operation.delete_operation(db, operation_id)
    return {"success": True}


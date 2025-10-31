from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_db
from app.schemas.process_state import ProcessStateSchema, ProcessStateCreate, ProcessStateUpdate
from app.crud import process_state, process_type

router = APIRouter()


@router.get("/types/{type_code}/states", response_model=List[ProcessStateSchema])
async def get_states_for_type(type_code: str, db: AsyncSession = Depends(get_db)):
    """Get all states for a type"""
    db_type = await process_type.get_by_code(db, type_code)
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    
    states = await process_state.get_by_type_id(db, db_type.id)
    return states


@router.get("/states/{state_id}", response_model=ProcessStateSchema)
async def get_state(state_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get single state"""
    state = await process_state.get_by_id(db, state_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    return state


@router.post("/types/{type_code}/states", response_model=ProcessStateSchema)
async def create_state(type_code: str, state_data: ProcessStateCreate, db: AsyncSession = Depends(get_db)):
    """Create new state"""
    db_type = await process_type.get_by_code(db, type_code)
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    
    return await process_state.create(db, state_data)


@router.put("/states/{state_id}", response_model=ProcessStateSchema)
async def update_state(state_id: UUID, state_data: ProcessStateUpdate, db: AsyncSession = Depends(get_db)):
    """Update state"""
    state = await process_state.update(db, state_id, state_data)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    return state


@router.delete("/states/{state_id}")
async def delete_state(state_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete state"""
    await process_state.delete_state(db, state_id)
    return {"success": True}


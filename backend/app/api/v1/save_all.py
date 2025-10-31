from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.schemas.save_all import SaveAllRequest, SaveAllResponse
from app.crud import process_type, process_state, process_operation

router = APIRouter()


@router.post("/save-all", response_model=SaveAllResponse)
async def save_all_changes(request: SaveAllRequest, db: AsyncSession = Depends(get_db)):
    """Save all pending changes in one transaction"""
    
    # Update/Create Type
    if request.type:
        existing = await process_type.get_by_code(db, request.type.code)
        if existing:
            await process_type.update(db, request.type.code, request.type)
        else:
            await process_type.create(db, request.type)
    
    # Process States
    if request.states:
        # Delete States
        for state_id in request.states.deleted:
            await process_state.delete_state(db, state_id)
        
        # Create States
        for state in request.states.created:
            await process_state.create(db, state)
        
        # Update States
        for state in request.states.updated:
            if hasattr(state, 'id'):
                state_id = getattr(state, 'id')
                await process_state.update(db, state_id, state)
    
    # Process Operations
    if request.operations:
        # Delete Operations
        for op_id in request.operations.deleted:
            await process_operation.delete_operation(db, op_id)
        
        # Create Operations
        for op in request.operations.created:
            await process_operation.create(db, op)
        
        # Update Operations
        for op in request.operations.updated:
            if hasattr(op, 'id'):
                op_id = getattr(op, 'id')
                await process_operation.update(db, op_id, op)
    
    # Update Operation-States relations
    if request.operation_states:
        for op_id_str, state_ids in request.operation_states.items():
            op_id = UUID(op_id_str)
            await process_operation.update_states(db, op_id, state_ids)
    
    return SaveAllResponse(success=True, message="All changes saved successfully")


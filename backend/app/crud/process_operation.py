from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.models.process_operation import ProcessOperation, ProcessOperationStates
from app.models.process_state import ProcessState
from app.schemas.process_operation import ProcessOperationCreate, ProcessOperationUpdate


async def get_by_type_id(db: AsyncSession, type_id: UUID) -> List[ProcessOperation]:
    result = await db.execute(
        select(ProcessOperation)
        .where(ProcessOperation.type_id == type_id)
        .options(selectinload(ProcessOperation.available_states))
    )
    return result.scalars().all()


async def get_by_id(db: AsyncSession, operation_id: UUID) -> Optional[ProcessOperation]:
    result = await db.execute(
        select(ProcessOperation)
        .where(ProcessOperation.id == operation_id)
        .options(selectinload(ProcessOperation.available_states))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, operation_data: ProcessOperationCreate) -> ProcessOperation:
    data = operation_data.model_dump(exclude={'available_state_ids'})
    db_operation = ProcessOperation(**data)
    db.add(db_operation)
    await db.flush()
    
    # Add available states
    if operation_data.available_state_ids:
        for state_id in operation_data.available_state_ids:
            db.add(ProcessOperationStates(operation_id=db_operation.id, state_id=state_id))
    
    await db.commit()
    await db.refresh(db_operation)
    return db_operation


async def update(db: AsyncSession, operation_id: UUID, operation_data: ProcessOperationUpdate) -> Optional[ProcessOperation]:
    db_operation = await get_by_id(db, operation_id)
    if db_operation:
        data = operation_data.model_dump(exclude_unset=True, exclude={'available_state_ids'})
        for key, value in data.items():
            setattr(db_operation, key, value)
        
        # Update available states if provided
        if operation_data.available_state_ids is not None:
            # Delete existing relations
            await db.execute(delete(ProcessOperationStates).where(ProcessOperationStates.operation_id == operation_id))
            # Add new relations
            for state_id in operation_data.available_state_ids:
                db.add(ProcessOperationStates(operation_id=operation_id, state_id=state_id))
        
        await db.commit()
        await db.refresh(db_operation)
    return db_operation


async def delete_operation(db: AsyncSession, operation_id: UUID) -> bool:
    await db.execute(delete(ProcessOperation).where(ProcessOperation.id == operation_id))
    await db.commit()
    return True


async def update_states(db: AsyncSession, operation_id: UUID, state_ids: List[UUID]) -> bool:
    # Delete existing relations
    await db.execute(delete(ProcessOperationStates).where(ProcessOperationStates.operation_id == operation_id))
    # Add new relations
    for state_id in state_ids:
        db.add(ProcessOperationStates(operation_id=operation_id, state_id=state_id))
    await db.commit()
    return True


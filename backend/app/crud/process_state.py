from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID

from app.models.process_state import ProcessState
from app.schemas.process_state import ProcessStateCreate, ProcessStateUpdate


async def get_by_type_id(db: AsyncSession, type_id: UUID) -> List[ProcessState]:
    result = await db.execute(select(ProcessState).where(ProcessState.type_id == type_id))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, state_id: UUID) -> Optional[ProcessState]:
    result = await db.execute(select(ProcessState).where(ProcessState.id == state_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, state_data: ProcessStateCreate) -> ProcessState:
    db_state = ProcessState(**state_data.model_dump())
    db.add(db_state)
    await db.commit()
    await db.refresh(db_state)
    return db_state


async def update(db: AsyncSession, state_id: UUID, state_data: ProcessStateUpdate) -> Optional[ProcessState]:
    db_state = await get_by_id(db, state_id)
    if db_state:
        for key, value in state_data.model_dump(exclude_unset=True).items():
            setattr(db_state, key, value)
        await db.commit()
        await db.refresh(db_state)
    return db_state


async def delete_state(db: AsyncSession, state_id: UUID) -> bool:
    await db.execute(delete(ProcessState).where(ProcessState.id == state_id))
    await db.commit()
    return True


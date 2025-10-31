from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.models.process_type import ProcessType
from app.schemas.process_type import ProcessTypeCreate


async def get_all(db: AsyncSession) -> List[ProcessType]:
    result = await db.execute(select(ProcessType))
    return result.scalars().all()


async def get_by_code(db: AsyncSession, code: str) -> Optional[ProcessType]:
    result = await db.execute(select(ProcessType).where(ProcessType.code == code))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, type_id: UUID) -> Optional[ProcessType]:
    result = await db.execute(select(ProcessType).where(ProcessType.id == type_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, type_data: ProcessTypeCreate) -> ProcessType:
    db_type = ProcessType(**type_data.model_dump())
    db.add(db_type)
    await db.commit()
    await db.refresh(db_type)
    return db_type


async def update(db: AsyncSession, code: str, type_data: ProcessTypeCreate) -> Optional[ProcessType]:
    db_type = await get_by_code(db, code)
    if db_type:
        for key, value in type_data.model_dump().items():
            setattr(db_type, key, value)
        await db.commit()
        await db.refresh(db_type)
    return db_type


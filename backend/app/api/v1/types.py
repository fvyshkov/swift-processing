from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db
from app.schemas.process_type import ProcessTypeSchema, ProcessTypeCreate
from app.crud import process_type

router = APIRouter()


@router.get("/types", response_model=List[ProcessTypeSchema])
async def get_types(db: AsyncSession = Depends(get_db)):
    """Get all process types"""
    types = await process_type.get_all(db)
    return types


@router.get("/types/{code}", response_model=ProcessTypeSchema)
async def get_type(code: str, db: AsyncSession = Depends(get_db)):
    """Get single type by code"""
    db_type = await process_type.get_by_code(db, code)
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    return db_type


@router.post("/types", response_model=ProcessTypeSchema)
async def create_type(type_data: ProcessTypeCreate, db: AsyncSession = Depends(get_db)):
    """Create new type"""
    return await process_type.create(db, type_data)


@router.put("/types/{code}", response_model=ProcessTypeSchema)
async def update_type(code: str, type_data: ProcessTypeCreate, db: AsyncSession = Depends(get_db)):
    """Update type"""
    db_type = await process_type.update(db, code, type_data)
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    return db_type


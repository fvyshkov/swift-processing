from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ProcessType(Base):
    __tablename__ = "process_type"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, unique=True, nullable=False)
    name_en = Column(Text, nullable=False)
    name_ru = Column(Text, nullable=False)
    attributes_table = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("process_type.id", ondelete="SET NULL"))
    
    # Relationships
    parent = relationship("ProcessType", remote_side=[id], backref="children")
    states = relationship("ProcessState", back_populates="type", cascade="all, delete-orphan")
    operations = relationship("ProcessOperation", back_populates="type", cascade="all, delete-orphan")


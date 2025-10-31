from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ProcessState(Base):
    __tablename__ = "process_state"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_id = Column(UUID(as_uuid=True), ForeignKey("process_type.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    name_en = Column(Text, nullable=False)
    name_ru = Column(Text, nullable=False)
    color_code = Column(Text)
    allow_edit = Column(Boolean, default=False)
    allow_delete = Column(Boolean, default=False)
    start = Column(Boolean, default=False)
    operation_list_script = Column(Text)
    
    # Relationships
    type = relationship("ProcessType", back_populates="states")


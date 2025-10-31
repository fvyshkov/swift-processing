from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ProcessOperationStates(Base):
    __tablename__ = "process_operation_states"
    
    operation_id = Column(UUID(as_uuid=True), ForeignKey("process_operation.id", ondelete="CASCADE"), primary_key=True)
    state_id = Column(UUID(as_uuid=True), ForeignKey("process_state.id", ondelete="CASCADE"), primary_key=True)


class ProcessOperation(Base):
    __tablename__ = "process_operation"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_id = Column(UUID(as_uuid=True), ForeignKey("process_type.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    name_en = Column(Text, nullable=False)
    name_ru = Column(Text, nullable=False)
    icon = Column(Text)
    resource_url = Column(Text)
    availability_condition = Column(Text)
    cancel = Column(Boolean, default=False)
    move_to_state_script = Column(Text)
    workflow = Column(Text)
    database = Column(Text)
    
    # Relationships
    type = relationship("ProcessType", back_populates="operations")
    available_states = relationship(
        "ProcessState",
        secondary="process_operation_states",
        backref="operations"
    )


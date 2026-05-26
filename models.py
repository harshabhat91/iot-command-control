from sqlalchemy import Column, String, DateTime
from datetime import datetime
from db import Base
import uuid

class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    status = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)

class CommandResponse(Base):
    __tablename__ = "command_responses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String)
    command = Column(String)
    result = Column(String)
    received_at = Column(DateTime, default=datetime.utcnow)
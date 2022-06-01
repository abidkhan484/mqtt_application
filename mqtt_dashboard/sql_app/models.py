from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class HomeIoTmodel(Base):
    __tablename__ = "sensors_data"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    device_id = Column(String)
    voltage = Column(String)
    current = Column(String)
    power = Column(String)
    status = Column(String)
    created_at = Column(String)


from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Stop(Base):
    __tablename__ = "stops"

    stop_id = Column(Integer, primary_key=True, index=True)
    stop_code = Column(String, nullable=True)
    stop_name = Column(String, nullable=True)
    stop_desc = Column(String, nullable=True)
    stop_lat = Column(Float, nullable=True)
    stop_lon = Column(Float, nullable=True)
    stop_url = Column(String, nullable=True)
    location_type = Column(Integer, nullable=True)
    parent_station = Column(String, nullable=True)
    stop_IBNR = Column(Integer, nullable=True)

    # Relationships
    stop_times = relationship("StopTime", back_populates="stop")
    transfers_from = relationship("Transfer", foreign_keys="Transfer.from_stop_id", back_populates="from_stop")
    transfers_to = relationship("Transfer", foreign_keys="Transfer.to_stop_id", back_populates="to_stop")
    reports = relationship("Report", back_populates="stop")
from sqlalchemy import Column, Integer, String, Time, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class StopTime(Base):
    __tablename__ = "stop_times"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(String, ForeignKey("trips.trip_id"), nullable=False)
    arrival_time = Column(Time, nullable=True)
    departure_time = Column(Time, nullable=True)
    stop_id = Column(Integer, ForeignKey("stops.stop_id"), nullable=False)
    stop_sequence = Column(Integer, nullable=False)
    stop_headsign = Column(String, nullable=True)
    pickup_type = Column(Integer, nullable=True)
    drop_off_type = Column(Integer, nullable=True)
    shape_dist_traveled = Column(Float, nullable=True)

    # Relationships
    trip = relationship("Trip", back_populates="stop_times")
    stop = relationship("Stop", back_populates="stop_times")
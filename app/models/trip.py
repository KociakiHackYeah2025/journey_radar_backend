from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(String, primary_key=True, index=True)
    route_id = Column(String, ForeignKey("routes.route_id"), nullable=True)
    service_id = Column(String, nullable=True)
    trip_headsign = Column(String, nullable=True)
    trip_short_name = Column(String, nullable=True)
    direction_id = Column(Integer, nullable=True)
    block_id = Column(String, nullable=True)
    shape_id = Column(String, nullable=True)
    wheelchair_accessible = Column(Integer, nullable=True)

    # Relationships
    route = relationship("Route", back_populates="trips")
    stop_times = relationship("StopTime", back_populates="trip")
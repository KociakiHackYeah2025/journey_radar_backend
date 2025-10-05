from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Route(Base):
    __tablename__ = "routes"

    route_id = Column(String, primary_key=True, index=True)
    agency_id = Column(String, ForeignKey("agencies.agency_id"), nullable=True)
    route_short_name = Column(String, nullable=True)
    route_long_name = Column(String, nullable=True)
    route_desc = Column(String, nullable=True)
    route_type = Column(Integer, nullable=True)
    route_url = Column(String, nullable=True)
    route_color = Column(String, nullable=True)
    route_text_color = Column(String, nullable=True)

    # Relationships - używam string reference żeby uniknąć circular import
    agency = relationship("Agency", back_populates="routes")
    trips = relationship("Trip", back_populates="route")
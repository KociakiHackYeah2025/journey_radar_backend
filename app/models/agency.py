from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Agency(Base):
    __tablename__ = "agencies"

    agency_id = Column(String, primary_key=True, index=True)
    agency_name = Column(String, nullable=True)
    agency_url = Column(String, nullable=True)
    agency_timezone = Column(String, nullable=True)
    agency_lang = Column(String, nullable=True)
    agency_phone = Column(String, nullable=True)
    agency_fare_url = Column(String, nullable=True)
    agency_email = Column(String, nullable=True)

    # Relationships
    routes = relationship("Route", back_populates="agency")
from sqlalchemy import Column, Integer, String
from app.database import Base

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)

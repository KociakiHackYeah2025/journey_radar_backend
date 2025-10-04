from sqlalchemy import Column, String, Float, Integer
from app.database import Base

class Shape(Base):
    __tablename__ = "shapes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shape_id = Column(String, nullable=False)
    shape_pt_lat = Column(Float, nullable=True)
    shape_pt_lon = Column(Float, nullable=True)
    shape_pt_sequence = Column(Integer, nullable=True)
    shape_dist_traveled = Column(Float, nullable=True)
from sqlalchemy import Column, Integer, String
from app.database import Base

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    point_name = Column(String, index=True, nullable=False)
    count = Column(Integer, default=1, nullable=False)

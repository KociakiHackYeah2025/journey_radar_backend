from sqlalchemy import Column, String, Date, Integer
from app.database import Base

class CalendarDate(Base):
    __tablename__ = "calendar_dates"

    service_id = Column(String, primary_key=True, index=True)
    date = Column(String, primary_key=True, index=True)
    exception_type = Column(Integer, nullable=True)
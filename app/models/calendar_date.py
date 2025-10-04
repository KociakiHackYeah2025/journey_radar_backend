from sqlalchemy import Column, String, Date, Integer
from app.database import Base

class CalendarDate(Base):
    __tablename__ = "calendar_dates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    exception_type = Column(Integer, nullable=False)
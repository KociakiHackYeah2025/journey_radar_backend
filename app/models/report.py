from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stop_id = Column(String, ForeignKey("stops.stop_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    boarded = Column(Boolean, default=False, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    dislikes = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="reports")
    stop = relationship("Stop", back_populates="reports")

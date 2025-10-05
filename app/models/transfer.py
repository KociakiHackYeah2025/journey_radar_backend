from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class Transfer(Base):
    __tablename__ = "transfers"

    from_stop_id = Column(String, ForeignKey("stops.stop_id"), primary_key=True, index=True)
    to_stop_id = Column(String, ForeignKey("stops.stop_id"), primary_key=True, index=True)
    transfer_type = Column(Integer, nullable=True)
    min_transfer_time = Column(Integer, nullable=True)

    # Relationships
    from_stop = relationship("Stop", foreign_keys=[from_stop_id], back_populates="transfers_from")
    to_stop = relationship("Stop", foreign_keys=[to_stop_id], back_populates="transfers_to")
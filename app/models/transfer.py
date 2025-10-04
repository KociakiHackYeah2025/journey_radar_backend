from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_stop_id = Column(Integer, ForeignKey("stops.stop_id"), nullable=False)
    to_stop_id = Column(Integer, ForeignKey("stops.stop_id"), nullable=False)
    transfer_type = Column(Integer, nullable=True)
    min_transfer_time = Column(Integer, nullable=True)

    # Relationships
    from_stop = relationship("Stop", foreign_keys=[from_stop_id], back_populates="transfers_from")
    to_stop = relationship("Stop", foreign_keys=[to_stop_id], back_populates="transfers_to")
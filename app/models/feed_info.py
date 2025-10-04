from sqlalchemy import Column, String, Date
from app.database import Base

class FeedInfo(Base):
    __tablename__ = "feed_info"

    id = Column(String, primary_key=True, index=True, default="default")
    feed_publisher_name = Column(String, nullable=False)
    feed_publisher_url = Column(String, nullable=True)
    feed_lang = Column(String, nullable=True)
    feed_start_date = Column(Date, nullable=True)
    feed_end_date = Column(Date, nullable=True)
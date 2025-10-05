# app/models/__init__.py
# Import wszystkich modeli, żeby SQLAlchemy je znalazło

from .user import User
from .place import Place
from .agency import Agency
from .route import Route
from .stop import Stop
from .trip import Trip
from .stop_time import StopTime
from .calendar_date import CalendarDate
from .shape import Shape
from .transfer import Transfer

from .feed_info import FeedInfo
from .report import Report

__all__ = [
    "User",
    "Place", 
    "Agency",
    "Route",
    "Stop",
    "Trip",
    "StopTime",
    "CalendarDate",
    "Shape",
    "Transfer",
    "FeedInfo",
    "Report"
]
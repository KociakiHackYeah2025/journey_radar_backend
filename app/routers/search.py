from fastapi import APIRouter, Query
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models.stop import Stop
from app.models.stop_time import StopTime
from app.models.calendar_date import CalendarDate
from app.models.trip import Trip
from app.models.search_history import SearchHistory
from typing import List

router = APIRouter()

@router.get("/search_history_top")
def search_history_top(db: Session = Depends(get_db)):
    top_history = db.query(SearchHistory).order_by(SearchHistory.count.desc()).limit(100).all()
    return [{"point_name": h.point_name, "count": h.count} for h in top_history]


@router.get("/search_autocomplete")
def search_autocomplete(
    query: str,
    db: Session = Depends(get_db)
):
    stops = db.query(Stop).filter(Stop.stop_name.ilike(f"%{query}%")).limit(10).all()
    return [stop.stop_name for stop in stops]

@router.get("/search")
def search(
    from_stop: str = Query(..., alias="from"),
    to_stop: str = Query(..., alias="to"),
    datetime_query: datetime = Query(..., alias="datetime"),
    db: Session = Depends(get_db)
):
    # Update search history for 'from_stop'
    from_history = db.query(SearchHistory).filter(SearchHistory.point_name == from_stop).first()
    if from_history:
        from_history.count += 1
    else:
        from_history = SearchHistory(point_name=from_stop, count=1)
        db.add(from_history)
    # Update search history for 'to_stop'
    to_history = db.query(SearchHistory).filter(SearchHistory.point_name == to_stop).first()
    if to_history:
        to_history.count += 1
    else:
        to_history = SearchHistory(point_name=to_stop, count=1)
        db.add(to_history)
    db.commit()
    # Find stop_ids for from and to
    from_stops = db.query(Stop).filter(Stop.stop_name == from_stop).all()
    to_stops = db.query(Stop).filter(Stop.stop_name == to_stop).all()
    from_stop_ids = [s.stop_id for s in from_stops]
    to_stop_ids = [s.stop_id for s in to_stops]

    # Find stop_times for from_stop_ids with departure_time >= datetime_query.time()
    stop_times_from = db.query(StopTime).filter(
        StopTime.stop_id.in_(from_stop_ids),
        StopTime.departure_time >= datetime_query.time()
    ).all()

    # Find trips for those stop_times
    trip_ids = [st.trip_id for st in stop_times_from]

    # Find stop_times for to_stop_ids and those trips
    stop_times_to = db.query(StopTime).filter(
        StopTime.stop_id.in_(to_stop_ids),
        StopTime.trip_id.in_(trip_ids)
    ).all()

    # Find trips that have both from and to stop_times
    valid_trip_ids = set([st.trip_id for st in stop_times_to]) & set(trip_ids)

    # Find calendar_dates for those trips and matching date
    trips = db.query(Trip).filter(Trip.trip_id.in_(valid_trip_ids)).all()
    results = []
    for trip in trips:
        calendar_date = db.query(CalendarDate).filter(
            CalendarDate.service_id == trip.service_id,
            CalendarDate.date == datetime_query.date()
        ).first()
        if calendar_date:
            results.append({
                "trip_id": trip.trip_id,
                "from_stop": from_stop,
                "to_stop": to_stop,
                "date": calendar_date.date
            })
    return results

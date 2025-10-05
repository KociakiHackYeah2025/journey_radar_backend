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
    results = []
    from app.models.stop_time import StopTime
    from app.models.trip import Trip
    from app.models.route import Route
    for stop in stops:
        stop_times = db.query(StopTime).filter(StopTime.stop_id == stop.stop_id).all()
        trip_ids = set(st.trip_id for st in stop_times)
        route_ids = set()
        route_info = []
        if trip_ids:
            trips = db.query(Trip).filter(Trip.trip_id.in_(trip_ids)).all()
            for trip in trips:
                route_ids.add(trip.route_id)
            if route_ids:
                routes = db.query(Route).filter(Route.route_id.in_(route_ids)).all()
                for route in routes:
                    route_info.append({
                        "route_id": route.route_id,
                        "route_short_name": route.route_short_name,
                        "route_long_name": route.route_long_name,
                        "route_type": route.route_type
                    })
        results.append({
            "stop_id": stop.stop_id,
            "stop_name": stop.stop_name,
            "routes": route_info
        })
    return results

@router.get("/search")
def search(
    from_stop: str = Query(..., alias="from_stop_id"),
    to_stop: str = Query(..., alias="to_stop_id"),
    datetime_query: datetime = Query(None, alias="datetime"),
    db: Session = Depends(get_db)
):
    if datetime_query is None:
        datetime_query = datetime.now()
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
    from_stop_ids = [from_stop]
    to_stop_ids = [to_stop]

    departure_time_str = datetime_query.time().strftime("%H:%M:%S")
    stop_times_from = db.query(StopTime).filter(
        StopTime.stop_id.in_(from_stop_ids),
        StopTime.departure_time >= departure_time_str
    ).all()
    trip_ids = [st.trip_id for st in stop_times_from]
    stop_times_to = db.query(StopTime).filter(
        StopTime.stop_id.in_(to_stop_ids),
        StopTime.trip_id.in_(trip_ids)
    ).all()

    valid_trip_ids = set()
    for st_from in stop_times_from:
        for st_to in stop_times_to:
            if st_from.trip_id == st_to.trip_id and st_from.stop_sequence < st_to.stop_sequence:
                valid_trip_ids.add(st_from.trip_id)

    trips = db.query(Trip).filter(Trip.trip_id.in_(valid_trip_ids)).all()
    results = []
    date_str = datetime_query.date().strftime("%Y-%m-%d")
    for trip in trips:
        calendar_date = db.query(CalendarDate).filter(
            CalendarDate.service_id == trip.service_id,
            CalendarDate.date == date_str
        ).first()
        if calendar_date:
            st_from = next((st for st in stop_times_from if st.trip_id == trip.trip_id), None)
            st_to = next((st for st in stop_times_to if st.trip_id == trip.trip_id), None)
            results.append({
                "trip_id": trip.trip_id,
                "route_id": trip.route_id,
                "date": calendar_date.date,
                "from_stop": {
                    "stop_id": from_stop,
                    "departure_time": st_from.departure_time if st_from else None,
                    "arrival_time": st_from.arrival_time if st_from else None,
                    "stop_sequence": st_from.stop_sequence if st_from else None
                },
                "to_stop": {
                    "stop_id": to_stop,
                    "departure_time": st_to.departure_time if st_to else None,
                    "arrival_time": st_to.arrival_time if st_to else None,
                    "stop_sequence": st_to.stop_sequence if st_to else None
                }
            })
    def time_key(item):
        t = item["from_stop"]["departure_time"]
        return t if t is not None else "99:99:99"
    results_sorted = sorted(results, key=time_key)
    return results_sorted

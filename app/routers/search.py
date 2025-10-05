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
from app.models.route import Route
from app.models.agency import Agency

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

router = APIRouter(tags=["Search"])

@router.get("/search_history_top", tags=["Search"])
def search_history_top(db: Session = Depends(get_db)):
    top_history = db.query(SearchHistory).order_by(SearchHistory.count.desc()).limit(100).all()
    return [{"point_name": h.point_name, "count": h.count} for h in top_history]

@router.get("/search_autocomplete", tags=["Search"])
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

@router.get("/search", tags=["Search"])
def search(
    from_stop: str = Query(..., alias="from_stop_id"),
    to_stop: str = Query(..., alias="to_stop_id"),
    datetime_query: datetime = Query(None, alias="datetime"),
    db: Session = Depends(get_db)
):
    if datetime_query is None:
        datetime_query = datetime.now()

    # Zapisz wyszukiwanie do historii
    for stop in [from_stop, to_stop]:
        history = db.query(SearchHistory).filter(SearchHistory.point_name == stop).first()
        if history:
            history.count += 1
        else:
            db.add(SearchHistory(point_name=stop, count=1))
    db.commit()

    # Pobierz stop_id dla from_stop i to_stop (może być przekazane jako nazwa lub id)
    from_stop_obj = db.query(Stop).filter((Stop.stop_id == from_stop) | (Stop.stop_name == from_stop)).first()
    to_stop_obj = db.query(Stop).filter((Stop.stop_id == to_stop) | (Stop.stop_name == to_stop)).first()
    if not from_stop_obj or not to_stop_obj:
        return {"error": "Nie znaleziono przystanku"}
    from_stop_id = from_stop_obj.stop_id
    to_stop_id = to_stop_obj.stop_id

    departure_time_str = datetime_query.strftime("%H:%M:%S")
    date_str = datetime_query.strftime("%Y%m%d")

    # Pobierz stop_times dla przystanku początkowego po zadanym czasie
    stop_times_from = db.query(StopTime).filter(
        StopTime.stop_id == from_stop_id,
        StopTime.departure_time >= departure_time_str
    ).all()
    trip_ids = [st.trip_id for st in stop_times_from]
    if not trip_ids:
        return []

    # Pobierz stop_times dla przystanku docelowego w tych samych tripach
    stop_times_to = db.query(StopTime).filter(
        StopTime.stop_id == to_stop_id,
        StopTime.trip_id.in_(trip_ids)
    ).all()

    # Filtruj tylko te tripy, gdzie przystanek początkowy jest przed docelowym
    valid_trip_ids = set()
    for st_from in stop_times_from:
        for st_to in stop_times_to:
            if st_from.trip_id == st_to.trip_id and st_from.stop_sequence < st_to.stop_sequence:
                valid_trip_ids.add(st_from.trip_id)

    if not valid_trip_ids:
        return []

    trips = db.query(Trip).filter(Trip.trip_id.in_(valid_trip_ids)).all()
    results = []
    for trip in trips:
        # Sprawdź czy kurs jest aktywny w danym dniu
        calendar_date = db.query(CalendarDate).filter(
            CalendarDate.service_id == trip.service_id,
            CalendarDate.date == date_str
        ).first()
        if not calendar_date:
            continue
        st_from = next((st for st in stop_times_from if st.trip_id == trip.trip_id), None)
        st_to = next((st for st in stop_times_to if st.trip_id == trip.trip_id), None)
        # Pobierz wszystkie stop_times dla tego tripa w kolejności
        all_stops_times = db.query(StopTime).filter(
            StopTime.trip_id == trip.trip_id
        ).order_by(StopTime.stop_sequence).all()
        # Wyciągnij przystanki od from do to (włącznie)
        stops_between = []
        if st_from and st_to:
            for st in all_stops_times:
                if st.stop_sequence >= st_from.stop_sequence and st.stop_sequence <= st_to.stop_sequence:
                    stop_obj = db.query(Stop).filter(Stop.stop_id == st.stop_id).first()
                    stops_between.append({
                        "stop_id": st.stop_id,
                        "stop_name": stop_obj.stop_name if stop_obj else None,
                        "stop_lat": stop_obj.stop_lat if stop_obj else None,
                        "stop_lon": stop_obj.stop_lon if stop_obj else None,
                        "stop_desc": stop_obj.stop_desc if stop_obj else None,
                        "arrival_time": st.arrival_time,
                        "departure_time": st.departure_time,
                        "stop_sequence": st.stop_sequence,
                        "pickup_type": st.pickup_type,
                        "drop_off_type": st.drop_off_type,
                        "stop_headsign": st.stop_headsign
                    })
        results.append({
            "trip_id": trip.trip_id,
            "route_id": trip.route_id,
            "date": calendar_date.date,
            "from_stop": {
                "stop_id": from_stop_id,
                "stop_name": from_stop_obj.stop_name,
                "departure_time": st_from.departure_time if st_from else None,
                "arrival_time": st_from.arrival_time if st_from else None,
                "stop_sequence": st_from.stop_sequence if st_from else None
            },
            "to_stop": {
                "stop_id": to_stop_id,
                "stop_name": to_stop_obj.stop_name,
                "departure_time": st_to.departure_time if st_to else None,
                "arrival_time": st_to.arrival_time if st_to else None,
                "stop_sequence": st_to.stop_sequence if st_to else None
            },
            "stops": stops_between
        })
    # Sortuj po czasie odjazdu
    results_sorted = sorted(results, key=lambda x: x["from_stop"]["departure_time"] or "99:99:99")
    return results_sorted

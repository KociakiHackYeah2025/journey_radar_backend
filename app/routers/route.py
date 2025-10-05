from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.trip import Trip
from app.models.report import Report
from app.models.route import Route

router = APIRouter(tags=["Route"])

@router.get("/route/{route_id}", tags=["Route"])
def get_route_info(route_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.route_id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Pobierz wszystkie tripy dla tej trasy
    trips = db.query(Trip).filter(Trip.route_id == route_id).all()
    trip_ids = [t.trip_id for t in trips]

    # Pobierz wszystkie stop_times dla tych tripów
    from app.models.stop_time import StopTime
    stop_times = db.query(StopTime).filter(StopTime.trip_id.in_(trip_ids)).all() if trip_ids else []
    stop_ids = set(st.stop_id for st in stop_times if st.stop_id)

    # Pobierz szczegóły przystanków
    from app.models.stop import Stop
    stops = db.query(Stop).filter(Stop.stop_id.in_(stop_ids)).all() if stop_ids else []
    # Dodaj czasy przyjazdu i odjazdu dla każdego przystanku
    stops_data = []
    for s in stops:
        # Filtruj stop_times dla danego przystanku
        times = [st for st in stop_times if st.stop_id == s.stop_id]
        # Jeśli jest wiele stop_times, wybierz pierwszy (lub można zwrócić wszystkie)
        arrival_time = times[0].arrival_time if times else None
        departure_time = times[0].departure_time if times else None
        stops_data.append({
            "stop_id": s.stop_id,
            "stop_name": s.stop_name,
            "stop_lat": s.stop_lat,
            "stop_lon": s.stop_lon,
            "arrival_time": arrival_time,
            "departure_time": departure_time
        })

    return {
        "route_id": route.route_id,
        "agency_id": route.agency_id,
        "route_short_name": route.route_short_name,
        "route_long_name": route.route_long_name,
        "route_desc": route.route_desc,
        "route_type": route.route_type,
        "route_url": route.route_url,
        "route_color": route.route_color,
        "route_text_color": route.route_text_color,
        "stops": stops_data
    }

@router.get("/route/{route_id}/delay", tags=["Route"])
def route_delay(route_id: str, db: Session = Depends(get_db)):
    # Pobierz wszystkie trip_id dla danej linii
    trips = db.query(Trip).filter(Trip.route_id == route_id).all()
    trip_ids = [t.trip_id for t in trips]
    # Pobierz wszystkie reporty dla tych trip_id
    reports = db.query(Report).filter(Report.trip_id.in_(trip_ids)).all() if trip_ids else []
    delays = []
    for r in reports:
        if r.boarded_time and r.created_at:
            delay = (r.boarded_time - r.created_at).total_seconds() // 60
            delays.append(delay)
    avg_delay = int(sum(delays) / len(delays)) if delays else None
    return {
        "route_id": route_id,
        "avg_delay_minutes": avg_delay,
        "reports_count": len(reports)
    }

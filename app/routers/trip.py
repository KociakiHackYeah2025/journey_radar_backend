from app.models.report import Report
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.stop import Stop
from app.models.stop_time import StopTime
from app.models.trip import Trip
from app.models.route import Route
from app.models.agency import Agency

router = APIRouter(tags=["Trip"])

@router.get("/trip/{trip_id}", tags=["Trip"])
def get_trip_info(trip_id: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        return {"error": "Nie znaleziono trip o podanym id"}

    route = db.query(Route).filter(Route.route_id == trip.route_id).first()
    agency = db.query(Agency).filter(Agency.agency_id == route.agency_id).first() if route else None

    stop_times = db.query(StopTime).filter(StopTime.trip_id == trip_id).order_by(StopTime.stop_sequence).all()
    stops = []
    for st in stop_times:
        stop = db.query(Stop).filter(Stop.stop_id == st.stop_id).first()
        stops.append({
            "stop_id": stop.stop_id if stop else st.stop_id,
            "stop_name": stop.stop_name if stop else None,
            "stop_lat": stop.stop_lat if stop else None,
            "stop_lon": stop.stop_lon if stop else None,
            "arrival_time": st.arrival_time,
            "departure_time": st.departure_time,
            "stop_sequence": st.stop_sequence,
            "pickup_type": st.pickup_type,
            "drop_off_type": st.drop_off_type,
            "stop_headsign": st.stop_headsign
        })

    result = {
        "trip_id": trip.trip_id,
        "route_id": trip.route_id,
        "service_id": trip.service_id,
        "trip_headsign": trip.trip_headsign,
        "trip_short_name": trip.trip_short_name,
        "direction_id": trip.direction_id,
        "block_id": trip.block_id,
        "shape_id": trip.shape_id,
        "wheelchair_accessible": trip.wheelchair_accessible,
        "route": {
            "route_id": route.route_id if route else None,
            "route_short_name": route.route_short_name if route else None,
            "route_long_name": route.route_long_name if route else None,
            "route_type": route.route_type if route else None,
            "route_desc": route.route_desc if route else None,
            "route_color": route.route_color if route else None,
            "route_text_color": route.route_text_color if route else None,
            "agency": {
                "agency_id": agency.agency_id if agency else None,
                "agency_name": agency.agency_name if agency else None,
                "agency_url": agency.agency_url if agency else None,
                "agency_timezone": agency.agency_timezone if agency else None,
                "agency_lang": agency.agency_lang if agency else None,
                "agency_phone": agency.agency_phone if agency else None,
                "agency_email": agency.agency_email if agency else None
            } if agency else None
        } if route else None,
        "stops": stops
    }
    return result


@router.get("/trip/{trip_id}/delay", tags=["Trip"])
def trip_delay(trip_id: str, db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.trip_id == trip_id, Report.boarded_time != None).all()
    delays = []
    for r in reports:
        if r.boarded_time and r.created_at:
            delay = (r.boarded_time - r.created_at).total_seconds() // 60
            delays.append(delay)
    avg_delay = int(sum(delays) / len(delays)) if delays else None
    return {
        "trip_id": trip_id,
        "avg_delay_minutes": avg_delay,
        "reports_count": len(reports),
        "reports": [
            {
                "id": r.id,
                "trip_id": r.trip_id,
                "boarded_time": r.boarded_time,
                "created_at": r.created_at,
                "user_id": r.user_id,
            } for r in reports
        ]
    }
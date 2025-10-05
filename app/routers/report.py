
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.models.user import User
from app.models.stop import Stop
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class ReportCreate(BaseModel):
    user_id: int
    stop_id: int
    boarded: bool
    created_at: Optional[datetime] = None

class RateReportRequest(BaseModel):
    helpful: bool

@router.post("/report/{report_id}/rate")
def rate_report(report_id: int, rate: RateReportRequest, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    user = db.query(User).filter(User.id == report.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if rate.helpful:
        user.points += 1
        report.likes += 1
    else:
        report.dislikes += 1
    db.commit()
    return {
        "user_id": user.id,
        "points": user.points,
        "report_id": report.id,
        "likes": report.likes,
        "dislikes": report.dislikes
    }


@router.post("/report")
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    # Optionally validate user and stop existence
    user = db.query(User).filter(User.id == report.user_id).first()
    stop = db.query(Stop).filter(Stop.stop_id == report.stop_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    new_report = Report(
        user_id=report.user_id,
        stop_id=report.stop_id,
        boarded=report.boarded,
        created_at=report.created_at or datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return {"id": new_report.id, "user_id": new_report.user_id, "stop_id": new_report.stop_id, "boarded": new_report.boarded, "created_at": new_report.created_at, "updated_at": new_report.updated_at}


@router.post("/report/{report_id}/rate")
def rate_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    user = db.query(User).filter(User.id == report.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.points += 1
    db.commit()
    return {"user_id": user.id, "points": user.points}

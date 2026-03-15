from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.report import EmergencyAlert, InterventionRecommendation, Report
from app.schemas.report import EmergencyAlertOut, InterventionRecommendationOut, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
def list_reports(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[Report]:
    query = db.query(Report)
    if user_id is not None:
        query = query.filter(Report.user_id == user_id)
    return query.order_by(Report.created_at.desc()).limit(limit).all()


@router.get("/by-session/{session_id}", response_model=ReportOut)
def get_report_by_session(session_id: int, db: Session = Depends(get_db)) -> Report:
    report = db.query(Report).filter(Report.session_id == session_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/frontend")
def get_report_frontend_shape(report_id: int, db: Session = Depends(get_db)) -> dict:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.report_json


@router.get("/session/{session_id}/recommendations", response_model=list[InterventionRecommendationOut])
def list_session_recommendations(session_id: int, db: Session = Depends(get_db)) -> list[InterventionRecommendation]:
    rows = (
        db.query(InterventionRecommendation)
        .filter(InterventionRecommendation.session_id == session_id)
        .order_by(InterventionRecommendation.priority.asc(), InterventionRecommendation.id.asc())
        .all()
    )
    return rows


@router.get("/alerts", response_model=list[EmergencyAlertOut])
def list_alerts(
    user_id: int | None = Query(default=None),
    session_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[EmergencyAlert]:
    query = db.query(EmergencyAlert)
    if user_id is not None:
        query = query.filter(EmergencyAlert.user_id == user_id)
    if session_id is not None:
        query = query.filter(EmergencyAlert.session_id == session_id)
    rows = query.order_by(EmergencyAlert.created_at.desc()).all()
    return rows

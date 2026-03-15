from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (UniqueConstraint("session_id", name="uk_reports_session"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    report_type: Mapped[str] = mapped_column(String(30), default="screening", nullable=False)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    report_pdf_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class InterventionRecommendation(Base):
    __tablename__ = "intervention_recommendations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    recommendation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("evaluation_sessions.id", ondelete="SET NULL"), nullable=True
    )
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    alert_title: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_content: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    is_handled: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    handled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

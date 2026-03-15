from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EmotionCheckin(Base):
    __tablename__ = "emotion_checkins"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mood_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    stress_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sleep_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    energy_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class MoodCalendarRecord(Base):
    __tablename__ = "mood_calendar_records"
    __table_args__ = (UniqueConstraint("user_id", "record_date", name="uk_mood_calendar_user_date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    mood_key: Mapped[str] = mapped_column(String(20), nullable=False)
    diary_text: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    weather_key: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    latest_risk_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    avg_mood_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    avg_stress_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    avg_sleep_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    phq9_latest_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

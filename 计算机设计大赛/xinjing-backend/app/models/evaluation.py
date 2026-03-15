from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class EvaluationSession(Base, TimestampMixin):
    __tablename__ = "evaluation_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="created", nullable=False)
    screening_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    used_modalities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    missing_modalities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    degraded_inference: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    overall_risk_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)


class SessionContextInfo(Base):
    __tablename__ = "session_context_info"
    __table_args__ = (UniqueConstraint("session_id", name="uk_context_session"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    recent_stress_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sleep_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    appetite_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    self_evaluation: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    social_avoidance_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    remark: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_url: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    format: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    upload_status: Mapped[str] = mapped_column(String(20), default="uploaded", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ModalityQualityMetric(Base):
    __tablename__ = "modality_quality_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    modality: Mapped[str] = mapped_column(String(20), nullable=False)
    quality_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    issue_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    modality: Mapped[str] = mapped_column(String(20), nullable=False)
    feature_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    feature_file_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ModelInferenceResult(Base):
    __tablename__ = "model_inference_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(60), nullable=False)
    fusion_strategy: Mapped[str] = mapped_column(String(60), nullable=False)
    face_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    voice_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    scale_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    text_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    fused_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    modality_weights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    missing_modalities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

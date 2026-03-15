from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class QuestionnaireTemplate(Base):
    __tablename__ = "questionnaire_templates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    total_score_rule: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(SmallInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class QuestionnaireQuestion(Base):
    __tablename__ = "questionnaire_questions"
    __table_args__ = (UniqueConstraint("template_id", "question_no", name="uk_template_question_no"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questionnaire_templates.id", ondelete="CASCADE"), nullable=False)
    question_no: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    score_mapping: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    question_type: Mapped[str] = mapped_column(String(32), default="single_choice", nullable=False)
    options_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uk_session_question"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questionnaire_templates.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questionnaire_questions.id", ondelete="CASCADE"), nullable=False)
    answer_value: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    answer_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class QuestionnaireResult(Base):
    __tablename__ = "questionnaire_results"
    __table_args__ = (UniqueConstraint("session_id", "template_id", name="uk_session_template_result"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questionnaire_templates.id", ondelete="CASCADE"), nullable=False)
    total_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    severity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    dimension_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

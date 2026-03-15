from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    evaluation_session_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("evaluation_sessions.id", ondelete="SET NULL"), nullable=True
    )
    session_topic: Mapped[str] = mapped_column(String(100), default="日常陪伴", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), default="text", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

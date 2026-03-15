from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    # DB stores hashed password in `password_hash`.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uk_user_profiles_user_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    age_range: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    education_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")

from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int]
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(40))
    intensity: Mapped[str] = mapped_column(String(20))
    fitness_level: Mapped[str] = mapped_column(String(20))
    equipment: Mapped[str] = mapped_column(String(40))
    duration: Mapped[int]
    access_token: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    plans: Mapped[list["Plan"]] = relationship(back_populates="user", order_by="Plan.id", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    user: Mapped[User] = relationship(back_populates="plans")

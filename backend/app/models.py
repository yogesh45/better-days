from datetime import datetime, date
from sqlalchemy import String, Text, Integer, Boolean, DateTime, Date, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str] = mapped_column(String(240), default="Building healthier days, one small step at a time.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(30), default="Other")
    cooking_minutes: Mapped[int] = mapped_column(Integer, default=20)
    servings: Mapped[int] = mapped_column(Integer, default=2)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredients: Mapped[list] = mapped_column(JSON, default=list)
    steps: Mapped[list] = mapped_column(JSON, default=list)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class HabitCheckin(Base):
    __tablename__ = "habit_checkins"
    __table_args__ = (UniqueConstraint("user_id", "habit_key", "checkin_date", name="uq_habit_day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    habit_key: Mapped[str] = mapped_column(String(40))
    checkin_date: Mapped[date] = mapped_column(Date, default=date.today)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)

class WaterLog(Base):
    __tablename__ = "water_logs"
    __table_args__ = (UniqueConstraint("user_id", "log_date", name="uq_water_day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    log_date: Mapped[date] = mapped_column(Date, default=date.today)
    glasses: Mapped[int] = mapped_column(Integer, default=0)

class CommunityPost(Base):
    __tablename__ = "community_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Cheer(Base):
    __tablename__ = "cheers"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_cheer_user_post"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)

class Challenge(Base):
    __tablename__ = "challenges"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    duration_days: Mapped[int] = mapped_column(Integer, default=7)

class ChallengeMembership(Base):
    __tablename__ = "challenge_memberships"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_membership"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

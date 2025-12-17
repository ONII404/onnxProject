# src/models/users.py
from datetime import datetime
from src.config.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from .enums import WatchStatus

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserLibrary(Base):
    __tablename__ = 'user_library'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    
    status = Column(Enum(WatchStatus), default=WatchStatus.PLANNED)
    score = Column(Integer)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    progress_details = relationship("UserProgress", back_populates="library_entry", cascade="all, delete-orphan")
    
    __table_args__ = (UniqueConstraint('user_id', 'series_id', name='_user_series_uc'),)

class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_library_id = Column(Integer, ForeignKey('user_library.id', ondelete='CASCADE'), nullable=False)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=False)
    
    chapters_read = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    last_read_at = Column(DateTime, default=datetime.utcnow)

    library_entry = relationship("UserLibrary", back_populates="progress_details")
    group = relationship("SeriesGroup")

    __table_args__ = (UniqueConstraint('user_library_id', 'group_id', name='_lib_group_uc'),)

__all__ = ["User", "UserLibrary", "UserProgress"]
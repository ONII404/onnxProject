# src/models/structure.py
from datetime import datetime
from src.config.db import Base
from sqlalchemy import Column, DateTime, Integer, String, Text, Float, Date, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from .enums import GroupType, ReleaseStatus

class SeriesGroup(Base):
    """Temporadas, Volúmenes o Partes"""
    __tablename__ = 'series_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(GroupType), nullable=False)
    order_number = Column(Float, nullable=False)
    
    title = Column(String(255))
    cover_url = Column(Text)
    status = Column(Enum(ReleaseStatus), default=ReleaseStatus.UNRELEASED)
    start_date = Column(Date)
    end_date = Column(Date)

    series = relationship("Series", back_populates="groups")
    chapters = relationship("Chapter", back_populates="group", cascade="all, delete-orphan")
    translations = relationship("GroupTranslation", back_populates="group", cascade="all, delete-orphan")
    external_links = relationship("ExternalLink", back_populates="group", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('series_id', 'type', 'order_number', name='_series_group_order_uc'),
    )

class Chapter(Base):
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=False)
    
    number_in_group = Column(Float, nullable=False)
    absolute_number = Column(Float, nullable=True)
    
    duration = Column(Integer)
    release_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("SeriesGroup", back_populates="chapters")
    translations = relationship("ChapterTranslation", back_populates="chapter", cascade="all, delete-orphan")

class GroupTranslation(Base):
    __tablename__ = 'group_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    title = Column(String(255))
    description = Column(Text)

    group = relationship("SeriesGroup", back_populates="translations")
    __table_args__ = (UniqueConstraint('group_id', 'language', name='_group_lang_uc'),)

class ChapterTranslation(Base):
    __tablename__ = 'chapter_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    title = Column(String(255))

    chapter = relationship("Chapter", back_populates="translations")
    __table_args__ = (UniqueConstraint('chapter_id', 'language', name='_chapter_lang_uc'),)

__all__ = ["SeriesGroup", "Chapter", "GroupTranslation", "ChapterTranslation"]
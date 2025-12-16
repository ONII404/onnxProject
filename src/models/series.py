from datetime import datetime
from src.config.db import Base
from sqlalchemy import Column, Integer, String, Table, Text, Boolean, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .enums import MediaType, SeriesStatus, RelationType

# Tabla intermedia para relación muchos-a-muchos con géneros
series_genres = Table(
    'series_genres', Base.metadata,
    Column('series_id', Integer, ForeignKey('series.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)
genres = relationship("Genre", secondary=series_genres, back_populates="genres")

class Series(Base):
    __tablename__ = 'series'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(MediaType), nullable=False)
    
    # Vital para JAV (IPX-123) y Libros (ISBN)
    reference_code = Column(String(50), index=True) 
    
    status = Column(Enum(SeriesStatus), default=SeriesStatus.ONGOING)
    is_adult = Column(Boolean, default=False)  # Filtro R18
    original_language = Column(String(5), default="ja")
    cover_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    genres = relationship("Genre", secondary=series_genres, back_populates="series")
    translations = relationship("SeriesTranslation", back_populates="series", cascade="all, delete-orphan")
    staff = relationship("SeriesStaff", back_populates="series", cascade="all, delete-orphan")
    groups = relationship("SeriesGroup", back_populates="series", cascade="all, delete-orphan")
    external_links = relationship("ExternalLink", back_populates="series", cascade="all, delete-orphan")

class SeriesTranslation(Base):
    __tablename__ = 'series_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    series = relationship("Series", back_populates="translations")
    __table_args__ = (UniqueConstraint('series_id', 'language', name='_series_lang_uc'),)

class SeriesRelation(Base):
    __tablename__ = 'series_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(RelationType), nullable=False)

    source = relationship("Series", foreign_keys=[source_id])
    target = relationship("Series", foreign_keys=[target_id])

    __table_args__ = (UniqueConstraint('source_id', 'target_id', name='_rel_source_target_uc'),)

__all__ = ["Series", "SeriesTranslation", "SeriesRelation"]
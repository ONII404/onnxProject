# src/models/genres.py
from src.config.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False)  # ej: "isekai", "ntr"
    
    translations = relationship("GenreTranslation", back_populates="genre", cascade="all, delete-orphan")

    series = relationship(
        "Series",
        secondary="series_genres",        # ← string, no variable
        back_populates="genres"
    )

class GenreTranslation(Base):
    __tablename__ = 'genre_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    genre_id = Column(Integer, ForeignKey('genres.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    name = Column(String(100), nullable=False)

    genre = relationship("Genre", back_populates="translations")
    __table_args__ = (UniqueConstraint('genre_id', 'language', name='_genre_lang_uc'),)

__all__ = ["Genre", "GenreTranslation", "series_genres"]
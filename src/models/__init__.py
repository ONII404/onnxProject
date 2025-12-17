# src/models/__init__.py
from src.config.db import Base
from .enums import (
    MediaType, WatchStatus, GroupType, SeriesStatus,
    ReleaseStatus, ExternalSource, StaffRole, RelationType
)


from .genres import Genre, GenreTranslation
from .series import Series, SeriesTranslation, SeriesRelation, series_genres
from .staff import People, Company, SeriesStaff
from .structure import SeriesGroup, Chapter, GroupTranslation, ChapterTranslation
from .users import User, UserLibrary, UserProgress
from .external import ExternalLink

__all__ = [
    "Base",

    # Enums
    "MediaType", "WatchStatus", "GroupType", "SeriesStatus",
    "ReleaseStatus", "ExternalSource", "StaffRole", "RelationType",

    # Tables
    "series_genres",

    # Models
    "Genre", "GenreTranslation", 
    "Series", "SeriesTranslation", "SeriesRelation",
    "People", "Company", "SeriesStaff",
    "SeriesGroup", "Chapter", "GroupTranslation", "ChapterTranslation",
    "User", "UserLibrary", "UserProgress",
    "ExternalLink",
]
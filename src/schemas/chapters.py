# src/schemas/chapters.py
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.schemas.common import TranslationCreate, TranslationResponse

# ===========================
# Chapter Schemas
# ===========================


class ChapterBase(BaseModel):
    number_in_group: float
    absolute_number: Optional[float] = None
    duration: Optional[int] = None  # Minutos o páginas
    release_date: Optional[date] = None


class ChapterCreate(ChapterBase):
    translations: Optional[List[TranslationCreate]] = None


class ChapterResponse(ChapterBase):
    id: int
    group_id: int
    translations: List[TranslationResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

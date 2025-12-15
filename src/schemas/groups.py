from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.schemas.common import ExternalLinkCreate, ExternalLinkResponse, TranslationCreate, TranslationResponse
from .enum import GroupType, ReleaseStatus


# =======================
# GRUPOS (Temporadas/Volúmenes) - Extensión de lo que ya tienes
# =======================
class GroupBase(BaseModel):
    type: GroupType
    order_number: float
    title: Optional[str] = None
    status: ReleaseStatus = ReleaseStatus.UNRELEASED
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cover_url: Optional[str] = None


class GroupCreate(GroupBase):
    translations: Optional[List[TranslationCreate]] = None
    external_links: Optional[List[ExternalLinkCreate]] = None


class GroupResponse(GroupBase):
    id: int
    series_id: int
    translations: List[TranslationResponse] = []
    external_links: List[ExternalLinkResponse] = []

    model_config = ConfigDict(from_attributes=True)

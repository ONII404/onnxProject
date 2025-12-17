# src/schemas/series.py
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from src.schemas.common import ExternalLinkCreate, ExternalLinkResponse, GenreCreate, GenreResponse, StaffCreate, StaffResponse, TranslationCreate, TranslationResponse
from src.schemas.groups import GroupCreate, GroupResponse
from .enum import MediaType, SeriesStatus

# =======================
# SERIES - Lo principal que pedías
# =======================

# Base: Campos esenciales comunes
class SeriesBase(BaseModel):
    type: MediaType
    reference_code: Optional[str] = None  # ej: IPX-123, ISBN
    status: SeriesStatus = SeriesStatus.ONGOING
    is_adult: bool = False
    original_language: str = "ja"
    cover_url: Optional[str] = None

# Create: Para POST /series (input del usuario)
# - Campos requeridos + opcionales
# - Incluye listas para crear relaciones en cascada (si usas session.add en el endpoint)
class SeriesCreate(SeriesBase):
    translations: List[TranslationCreate]  # Al menos uno? Hazlo required si quieres
    genres: Optional[List[GenreCreate]] = None  # Slugs para asociar
    staff: Optional[List[StaffCreate]] = None
    groups: Optional[List[GroupCreate]] = None  # Puedes crear groups al mismo tiempo
    external_links: Optional[List[ExternalLinkCreate]] = None

# Update: Para PATCH /series/{id} (updates parciales)
# - Todo opcional, para no sobreescribir lo que no se envíe
class SeriesUpdate(BaseModel):
    type: Optional[MediaType] = None
    reference_code: Optional[str] = None
    status: Optional[SeriesStatus] = None
    is_adult: Optional[bool] = None
    original_language: Optional[str] = None
    cover_url: Optional[str] = None
    # Para relaciones: Si quieres actualizarlas, usa listas opcionales
    # Pero para updates complejos de relaciones, mejor endpoints separados (ej: POST /series/{id}/genres)

# Response Básico: Para listas o detalles simples (tu getSeriesById)
class SeriesPublic(SeriesBase):
    id: int
    created_at: datetime
    translations: List[TranslationResponse] = []  # Incluye títulos/descripciones
    genres: List[GenreResponse] = []

    model_config = ConfigDict(from_attributes=True)

# Response Completo: Para detalles full (tu getSeriesFullById)
# - Incluye todo: groups con capítulos, staff, etc.
class SeriesFull(SeriesPublic):
    staff: List[StaffResponse] = []
    groups: List[GroupResponse] = []  # Groups incluyen chapters si los anidas en GroupResponse
    external_links: List[ExternalLinkResponse] = []

    model_config = ConfigDict(from_attributes=True)

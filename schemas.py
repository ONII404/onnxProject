from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class MediaType(str, Enum):
    ANIME = "anime"
    MANGA = "manga"
    NOVEL = "novel"
    JAV = "jav"
    DOUJIN = "doujin"

class SeriesStatus(str, Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    HIATUS = "hiatus"

class ReleaseStatus(str, Enum):
    FINISHED = "finished"
    RELEASING = "releasing"
    ANNOUNCED = "announced"
    UNRELEASED = "unreleased"

class GroupType(str, Enum):
    SEASON = "season"
    VOLUME = "volume"
    PART = "part"
    ABSOLUTE = "absolute"

class StaffRole(str, Enum):
    DIRECTOR = "director"
    WRITER = "writer"
    MUSIC = "music"
    STUDIO = "studio"
    MAKER = "maker"
    PUBLISHER = "publisher"
    CIRCLE = "circle"
    ACTRESS = "actress"
    VOICE_ACTOR = "voice_actor"
    MANGAKA = "mangaka"

class ExternalSource(str, Enum):
    MYANIMELIST = "myanimelist"
    ANILIST = "anilist"
    KITSU = "kitsu"
    MANGAUPDATES = "mangaupdates"
    DMM = "dmm"
    JAVLIBRARY = "javlibrary"

# =======================
# AUXILIARES (Para Relaciones)
# =======================

# Géneros (simplificado)
class GenreBase(BaseModel):
    slug: str  # ej: "isekai"

class GenreCreate(GenreBase):
    pass

class GenreResponse(GenreBase):
    id: int
    name: Optional[str] = None  # Si usas translations, puedes anidarlas aquí

    model_config = ConfigDict(from_attributes=True)

# Traducciones (genérico para Series, Groups, etc.)
class TranslationBase(BaseModel):
    language: str  # ej: "en", "es"
    title: str
    description: Optional[str] = None

class TranslationCreate(TranslationBase):
    pass

class TranslationResponse(TranslationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Staff (Personas o Compañías)
class StaffBase(BaseModel):
    role: StaffRole
    role_detail: Optional[str] = None
    # Para person_id o company_id: Usa uno u otro
    person_id: Optional[int] = None
    company_id: Optional[int] = None

class StaffCreate(StaffBase):
    pass

class StaffResponse(StaffBase):
    id: int
    # Puedes anidar details de Person o Company si lo necesitas
    # Ej: person: Optional[PersonResponse] = None

    model_config = ConfigDict(from_attributes=True)

# Enlaces Externos
class ExternalLinkBase(BaseModel):
    source: ExternalSource
    external_id: str
    url: Optional[str] = None

class ExternalLinkCreate(ExternalLinkBase):
    pass

class ExternalLinkResponse(ExternalLinkBase):
    id: int
    last_synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# =======================
# USUARIOS
# =======================

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str  # Necesario para registro

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Opcional en updates

class UserResponse(UserBase):
    id: int
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}  # Antes era class Config

# Opcional: para login
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

# =======================
# CAPÍTULOS - Extensión de lo que ya tienes
# =======================
class ChapterBase(BaseModel):
    number_in_group: float
    absolute_number: Optional[float] = None
    duration: Optional[int] = None  # Minutos o páginas
    release_date: Optional[date] = None

class ChapterCreate(ChapterBase):
    translations: Optional[List[TranslationCreate]] = None  # Solo title por capítulo

class ChapterResponse(ChapterBase):
    id: int
    group_id: int
    translations: List[TranslationResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

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

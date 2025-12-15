from datetime import datetime, date
from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.schemas.enum import ExternalSource, StaffRole


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






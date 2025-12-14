from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from datetime import date

# =======================
# USUARIOS
# =======================
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# =======================
# SERIES
# =======================
class SeriesBase(BaseModel):
    type: str  # anime, manga, novel, etc.
    is_adult: bool = False

# Input (Lo que envías al crear)
class SeriesCreate(SeriesBase):
    title: str       # El título lo pasaremos a la tabla de traducciones
    reference_code: str # Código interno (ej: ISBN, IPX)
    description: Optional[str] = None

# Output Público (Lo que ve todo el mundo)
class SeriesPublic(SeriesBase):
    id: int
    # No mostramos reference_code ni fechas de creación
    # Nota: Para mostrar el título aquí se requiere un poco más de lógica avanzada con SQLAlchemy 
    # (hybrid properties), por ahora devolveremos el objeto base.
    
    class Config:
        from_attributes = True

# Output Admin (Lo que ves tú)
class SeriesAdmin(SeriesBase):
    id: int
    reference_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# =======================
# GRUPOS (Temporadas/Volúmenes)
# =======================
class GroupBase(BaseModel):
    type: str # season, volume, etc.
    order_number: float
    title: Optional[str] = None
    status: str = "unreleased" # unreleased, releasing, finished
    start_date: Optional[date] = None

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: int
    series_id: int
    class Config:
        from_attributes = True

# =======================
# CAPÍTULOS
# =======================
class ChapterBase(BaseModel):
    number_in_group: float
    absolute_number: Optional[float] = None
    duration: Optional[int] = None # Páginas o minutos
    release_date: Optional[date] = None

class ChapterCreate(ChapterBase):
    pass

class ChapterResponse(ChapterBase):
    id: int
    group_id: int
    class Config:
        from_attributes = True
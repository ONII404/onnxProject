from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Imports absolutos (desde la raíz del proyecto)
import models
import database
import schemas
import auth

router = APIRouter(
    prefix="/series",
    tags=["Series"]
)

# ==========================================
#  ZONA PÚBLICA (GET - Lectura)
# ==========================================

# GET: Obtener una Serie por ID (Basica)
@router.get("/{id}", response_model=schemas.SeriesPublic, summary="getSeriesById")
def getSeriesById(id: int, db: Session = Depends(database.get_db)):
    serie = db.query(models.Series).filter(models.Series.id == id).first()
    if not serie:
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    return serie

# GET: Obtener una Serie por ID (Completa)
@router.get("/{id}/full", response_model=schemas.SeriesPublic, summary="getSeriesFullById")
def getSeriesFullById(id: int, db: Session = Depends(database.get_db)):
    """Obtener una Serie por su ID con toda la información relacionada (traducciones, grupos, episodios/capítulos)"""
    serie = db.query(models.Series).filter(models.Series.id == id).first()
    if not serie:
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    return serie

# Get: Obtener Series por tipo (MediaType)
@router.get("/type/{media_type}", response_model=List[schemas.SeriesPublic], summary="getSeriesByType")
def get_series_by_type(media_type: str, db: Session = Depends(database.get_db)):
    """Obtener series filtrando por tipo de medio (anime, manga, novel...)"""
    try:
        media_type_enum = models.MediaType(media_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo inválido (anime, manga, novel...)")
    
    return db.query(models.Series).filter(
        models.Series.type == media_type_enum,
        models.Series.is_adult == False
    ).all()


# ==========================================
#  ZONA ADMIN (POST/DELETE - Escritura)
# ==========================================

@router.post("/", response_model=schemas.SeriesAdmin)
def create_series(
    serie: schemas.SeriesCreate, 
    db: Session = Depends(database.get_db),
    user: str = Depends(auth.get_current_user) # <--- CANDADO DE SEGURIDAD
):
    # 1. Validar el tipo de medio
    try:
        media_type_enum = models.MediaType(serie.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo inválido (anime, manga, novel...)")

    # 2. Crear la Serie (El contenedor principal)
    db_series = models.Series(
        type=media_type_enum,
        reference_code=serie.reference_code,
        is_adult=serie.is_adult
    )
    db.add(db_series)
    db.commit()
    db.refresh(db_series) # Obtenemos el ID generado

    # 3. Crear la Traducción (Título y Descripción) automáticamente
    # Como tu DB separa el título en otra tabla, debemos guardarlo ahí.
    # Asumimos idioma por defecto 'es' (Español) o 'ja' (Japonés) según prefieras.
    db_translation = models.SeriesTranslation(
        series_id=db_series.id,
        language="es",  # Idioma por defecto para la creación rápida
        title=serie.title,
        description=serie.description
    )
    db.add(db_translation)
    db.commit()
    
    return db_series

# POST: Agregar Temporada/Volumen a una Serie
# URL: POST /series/1/groups
@router.post("/{series_id}/groups", response_model=schemas.GroupResponse)
def create_group_for_series(
    series_id: int,
    group: schemas.GroupCreate,
    db: Session = Depends(database.get_db),
    user: str = Depends(auth.get_current_user)
):
    db_series = db.query(models.Series).filter(models.Series.id == series_id).first()
    if not db_series:
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    try:
        group_type = models.GroupType(group.type)
        release_status = models.ReleaseStatus(group.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tipo o status inválido")

    db_group = models.SeriesGroup(
        series_id=series_id,
        type=group_type,
        order_number=group.order_number,
        title=group.title,
        status=release_status,
        start_date=group.start_date
    )
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group
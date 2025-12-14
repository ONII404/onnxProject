from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Imports absolutos
import models
import database
import schemas
import auth

router = APIRouter(
    prefix="/groups",
    tags=["Groups (Seasons/Volumes)"]
)

# GET: Ver detalle de un grupo (y sus capítulos)
# URL: GET /groups/50
@router.get("/{group_id}", response_model=schemas.GroupResponse)
def read_group(group_id: int, db: Session = Depends(database.get_db)):
    db_group = db.query(models.SeriesGroup).filter(models.SeriesGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return db_group

# POST: Agregar un Capítulo a este Grupo
# URL: POST /groups/50/chapters
@router.post("/{group_id}/chapters", response_model=schemas.ChapterResponse)
def create_chapter(
    group_id: int,
    chapter: schemas.ChapterCreate,
    db: Session = Depends(database.get_db),
    user: str = Depends(auth.get_current_user) # CANDADO
):
    # 1. Verificar que el grupo exista
    db_group = db.query(models.SeriesGroup).filter(models.SeriesGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")

    # 2. Crear Capítulo
    db_chapter = models.Chapter(
        group_id=group_id,
        number_in_group=chapter.number_in_group,
        absolute_number=chapter.absolute_number,
        duration=chapter.duration,
        release_date=chapter.release_date
    )

    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter
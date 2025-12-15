# routers/series.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from src.schemas import groups as schemaGroups 
from src.schemas import series as schemaSeries
from src.schemas import chapters as schemaChapters
from src.models import models as models
from src import dependencies as database
from src import dependencies as auth

series = APIRouter(
    prefix="/series",
    tags=["Series"]
)


# ==========================================
#  LECTURA PÚBLICA
# ==========================================

@series.get("/", response_model=List[schemaSeries.SeriesPublic], summary="Listar series con filtros")
def list_series(
    type: Optional[str] = None,
    search: Optional[str] = Query(None, min_length=1, description="Search by title"),
    genre: Optional[str] = None,
    adult: bool = False,  # Por defecto ocultar contenido R18
    limit: int = Query(20, ge=1, le=100), 
    offset: int = Query(0, ge=0),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Series)

    # Filter by type (anime, manga, etc.)
    if type:
        try:
            media_type = models.MediaType(type.lower())
            query = query.filter(models.Series.type == media_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Tipo inválido. Opciones: anime, manga, novel, jav, doujin")

    # Hide adult content if not requested
    if not adult:
        query = query.filter(models.Series.is_adult == False)

    # Shearch by title in translations
    if search:
        query = query.join(models.SeriesTranslation).filter(
            models.SeriesTranslation.title.ilike(f"%{search}%")
        )

    # Filter by genre slug
    if genre:
        query = query.join(models.series_genres).join(models.Genre).filter(
            models.Genre.slug == genre.lower()
        )

    return query.offset(offset).limit(limit).all()


@series.get("/{id}", response_model=schemaSeries.SeriesPublic, summary="Obtener serie básica por ID")
def get_series(id: int, db: Session = Depends(database.get_db)):
    serie = db.query(models.Series).filter(models.Series.id == id).first()
    if not serie:
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    return serie


@series.get("/{id}/full", response_model=schemaSeries.SeriesFull, summary="Obtener serie completa con todo")
def get_series_full(id: int, db: Session = Depends(database.get_db)):
    serie = (
        db.query(models.Series)
        .options(
            joinedload(models.Series.translations),
            joinedload(models.Series.genres),
            joinedload(models.Series.staff),
            joinedload(models.Series.external_links),
            joinedload(models.Series.groups).joinedload(models.SeriesGroup.translations),
            joinedload(models.Series.groups).joinedload(models.SeriesGroup.chapters).joinedload(models.Chapter.translations),
        )
        .filter(models.Series.id == id)
        .first()
    )
    if not serie:
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    return serie


# ==========================================
#  GESTIÓN DE SERIES (Solo Admin)
# ==========================================

@series.post("/", response_model=schemaSeries.SeriesPublic, status_code=status.HTTP_201_CREATED, summary="Crear nueva serie")
def create_series(
    data: schemaSeries.SeriesCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user)
):
    db_series = models.Series(
        type=data.type,
        reference_code=data.reference_code,
        status=data.status,
        is_adult=data.is_adult,
        original_language=data.original_language,
        cover_url=data.cover_url,
    )
    db.add(db_series)
    db.flush()  # Obtiene el ID

    # Traducciones
    for trans in data.translations:
        db.add(models.SeriesTranslation(
            series_id=db_series.id,
            language=trans.language,
            title=trans.title,
            description=trans.description
        ))

    # Géneros por slug
    if data.genres:
        for g in data.genres:
            genre = db.query(models.Genre).filter(models.Genre.slug == g.slug).first()
            if genre:
                db_series.genres.append(genre)
            # Opcional: crear género si no existe?

    db.commit()
    db.refresh(db_series)
    return db_series


@series.patch("/{id}", response_model=schemaSeries.SeriesPublic, summary="Actualizar serie (parcial)")
def update_series(
    id: int,
    data: schemaSeries.SeriesUpdate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user)
):
    db_series = db.query(models.Series).filter(models.Series.id == id).first()
    if not db_series:
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_series, key, value)

    db.commit()
    db.refresh(db_series)
    return db_series


@series.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar serie")
def delete_series(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user)
):
    db_series = db.query(models.Series).filter(models.Series.id == id).first()
    if not db_series:
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    db.delete(db_series)
    db.commit()
    return None


# ==========================================
#  GRUPOS (Temporadas, Volúmenes, etc.)
# ==========================================

@series.get("/{series_id}/groups", response_model=List[schemaGroups.GroupResponse], summary="Listar grupos de una serie")
def get_groups_by_series(series_id: int, db: Session = Depends(database.get_db)):
    if not db.query(models.Series).filter(models.Series.id == series_id).first():
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    
    return db.query(models.SeriesGroup).filter(models.SeriesGroup.series_id == series_id).all()


@series.post("/{series_id}/groups", response_model=schemaGroups.GroupResponse, summary="Crear grupo (temporada/volumen)")
def create_group(
    series_id: int,
    group_data: schemaGroups.GroupCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user)
):
    if not db.query(models.Series).filter(models.Series.id == series_id).first():
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    db_group = models.SeriesGroup(
        series_id=series_id,
        type=group_data.type,
        order_number=group_data.order_number,
        title=group_data.title,
        cover_url=group_data.cover_url,
        status=group_data.status,
        start_date=group_data.start_date,
        end_date=group_data.end_date,
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    # Traducciones del grupo
    if getattr(group_data, "translations", None):
        for trans in group_data.translations:
            db.add(models.GroupTranslation(
                group_id=db_group.id,
                language=trans.language,
                title=trans.title,
                description=trans.description
            ))
        db.commit()

    return db_group


# ==========================================
#  CAPÍTULOS
# ==========================================

@series.get("/{series_id}/groups/{group_id}/chapters", response_model=List[schemaChapters.ChapterResponse], summary="Listar capítulos de un grupo")
def get_chapters_by_group(series_id: int, group_id: int, db: Session = Depends(database.get_db)):
    db_group = db.query(models.SeriesGroup).filter(
        models.SeriesGroup.id == group_id,
        models.SeriesGroup.series_id == series_id
    ).first()
    
    if not db_group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado o no pertenece a esta serie")
    
    return db_group.chapters


@series.post("/{series_id}/groups/{group_id}/chapters", response_model=schemaChapters.ChapterResponse, summary="Crear capítulo")
def create_chapter(
    series_id: int,
    group_id: int,
    chapter_data: schemaChapters.ChapterCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user)
):
    db_group = db.query(models.SeriesGroup).filter(
        models.SeriesGroup.id == group_id,
        models.SeriesGroup.series_id == series_id
    ).first()
    
    if not db_group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado o no pertenece a esta serie")

    db_chapter = models.Chapter(
        group_id=group_id,
        number_in_group=chapter_data.number_in_group,
        absolute_number=chapter_data.absolute_number,
        duration=chapter_data.duration,
        release_date=chapter_data.release_date,
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)

    # Traducciones del capítulo
    if getattr(chapter_data, "translations", None):
        for trans in chapter_data.translations:
            db.add(models.ChapterTranslation(
                chapter_id=db_chapter.id,
                language=trans.language,
                title=trans.title
            ))
        db.commit()

    return db_chapter
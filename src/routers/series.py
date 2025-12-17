# routers/series.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from src.schemas import groups as schemaGroups
from src.schemas import series as schemaSeries
from src.schemas import chapters as schemaChapters
from src.models import enums as modelsEnums
from src.models import series as modelsSeries
from src.models import genres as modelsGenres
from src.models import structure as modelsStructure
from src.config import db as database
from src.config import auth

series = APIRouter(prefix="/series", tags=["Series"])


# obtener lista de series con filtros
@series.get(
    "/",
    response_model=List[schemaSeries.SeriesPublic],
    summary="Listar series con filtros",
)
def list_series(
    type: Optional[str] = None,
    search: Optional[str] = Query(None, min_length=1, description="Search by title"),
    genre: Optional[str] = None,
    adult: bool = False,  # Por defecto ocultar contenido R18
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(database.get_db),
):
    query = db.query(modelsSeries.Series)

    # Filter by type (anime, manga, etc.)
    if type:
        try:
            media_type = modelsEnums.MediaType(type.lower())
            query = query.filter(modelsSeries.Series.type == media_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Tipo inválido. Opciones: anime, manga, novel, jav, doujin",
            )

    # Hide adult content if not requested
    if not adult:
        query = query.filter(modelsSeries.Series.is_adult == False)

    # Shearch by title in translations
    if search:
        query = query.join(modelsSeries.SeriesTranslation).filter(
            modelsSeries.SeriesTranslation.title.ilike(f"%{search}%")
        )

    # Filter by genre slug
    if genre:
        query = query.join(modelsSeries.Series.genres).filter(
            modelsGenres.Genre.slug == genre.lower()
        )

    return query.offset(offset).limit(limit).all()


# obtener una serie por id
@series.get(
    "/{id}",
    response_model=schemaSeries.SeriesPublic,
    summary="Obtener serie básica por ID",
)
def get_series(id: int, db: Session = Depends(database.get_db)):
    serie = db.query(modelsSeries.Series).filter(modelsSeries.Series.id == id).first()
    if not serie:
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    return serie


# obtener una serie completa por id (con todo lo relacionado)
@series.get(
    "/{id}/full",
    response_model=schemaSeries.SeriesFull,
    summary="Obtener serie completa con todo",
)
def get_series_full(id: int, db: Session = Depends(database.get_db)):
    serie = (
        db.query(modelsSeries.Series)
        .options(
            joinedload(modelsSeries.Series.translations),
            joinedload(modelsSeries.Series.genres),
            joinedload(modelsSeries.Series.staff),
            joinedload(modelsSeries.Series.external_links),
            joinedload(modelsSeries.Series.groups).joinedload(
                modelsStructure.SeriesGroup.translations
            ),
            joinedload(modelsSeries.Series.groups)
            .joinedload(modelsStructure.SeriesGroup.chapters)
            .joinedload(modelsStructure.Chapter.translations),
        )
        .filter(modelsSeries.Series.id == id)
        .first()
    )
    if not serie:
        raise HTTPException(status_code=404, detail="Serie no encontrada")
    return serie


# ==========================================
#  GESTIÓN DE SERIES (Solo Admin)
# ==========================================


# crear nueva serie (parcial)
@series.post(
    "/partial",
    response_model=schemaSeries.SeriesPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva serie (parcial)",
)
def create_serie_Partial(
    data: schemaSeries.SeriesBase,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
):
    db_series = modelsSeries.Series(
        type=data.type,
        reference_code=data.reference_code,
        status=data.status,
        is_adult=data.is_adult,
        original_language=data.original_language,
        cover_url=data.cover_url,
    )
    db.add(db_series)
    db.commit()
    db.refresh(db_series)
    f"Serie creada con ID {db_series.id}"
    return db_series


# crear nueva serie (completa)
@series.post(
    "/Full",
    response_model=schemaSeries.SeriesPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva serie",
)
def create_serie_Full(
    data: schemaSeries.SeriesCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
):
    db_series = modelsSeries.Series(
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
        db.add(
            modelsSeries.SeriesTranslation(
                series_id=db_series.id,
                language=trans.language,
                title=trans.title,
                description=trans.description,
            )
        )

    # Géneros por slug
    if data.genres:
        for g in data.genres:
            genre = (
                db.query(modelsGenres.Genre)
                .filter(modelsGenres.Genre.slug == g.slug)
                .first()
            )
            if genre:
                db_series.genres.append(genre)
            # Opcional: crear género si no existe?

    db.commit()
    db.refresh(db_series)
    return db_series


# actualizar serie (parcial)
@series.patch(
    "/{id}",
    response_model=schemaSeries.SeriesPublic,
    summary="Actualizar serie (parcial)",
)
def update_series(
    id: int,
    data: schemaSeries.SeriesUpdate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
):
    db_series = (
        db.query(modelsSeries.Series).filter(modelsSeries.Series.id == id).first()
    )
    if not db_series:
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_series, key, value)

    db.commit()
    db.refresh(db_series)
    return db_series


# eliminar serie
@series.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar serie"
)
def delete_series(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
):
    db_series = (
        db.query(modelsSeries.Series).filter(modelsSeries.Series.id == id).first()
    )
    if not db_series:
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    db.delete(db_series)
    db.commit()
    return None


# ==========================================
#  GRUPOS (Temporadas, Volúmenes, etc.)
# ==========================================


@series.get(
    "/{series_id}/groups",
    response_model=List[schemaGroups.GroupResponse],
    summary="Listar grupos de una serie",
)
def get_groups_by_series(series_id: int, db: Session = Depends(database.get_db)):
    if (
        not db.query(modelsSeries.Series)
        .filter(modelsSeries.Series.id == series_id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    return (
        db.query(modelsStructure.SeriesGroup)
        .filter(modelsStructure.SeriesGroup.series_id == series_id)
        .all()
    )


@series.post(
    "/{series_id}/groups",
    response_model=schemaGroups.GroupResponse,
    summary="Crear grupo (temporada/volumen)",
)
def create_group(
    series_id: int,
    group_data: schemaGroups.GroupCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
):
    if (
        not db.query(modelsSeries.Series)
        .filter(modelsSeries.Series.id == series_id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Serie no encontrada")

    db_group = modelsStructure.SeriesGroup(
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
            db.add(
                modelsStructure.GroupTranslation(
                    group_id=db_group.id,
                    language=trans.language,
                    title=trans.title,
                    description=trans.description,
                )
            )
        db.commit()

    return db_group


# ==========================================
#  CAPÍTULOS
# ==========================================


@series.get(
    "/{series_id}/groups/{group_id}/chapters",
    response_model=List[schemaChapters.ChapterResponse],
    summary="Listar capítulos de un grupo",
)
def get_chapters_by_group(
    series_id: int, group_id: int, db: Session = Depends(database.get_db)
):
    db_group = (
        db.query(modelsStructure.SeriesGroup)
        .filter(
            modelsStructure.SeriesGroup.id == group_id,
            modelsStructure.SeriesGroup.series_id == series_id,
        )
        .first()
    )

    if not db_group:
        raise HTTPException(
            status_code=404, detail="Grupo no encontrado o no pertenece a esta serie"
        )

    return db_group.chapters


@series.post(
    "/{series_id}/groups/{group_id}/chapters",
    response_model=schemaChapters.ChapterResponse,
    summary="Crear capítulo",
)
def create_chapter(
    series_id: int,
    group_id: int,
    chapter_data: schemaChapters.ChapterCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
):
    db_group = (
        db.query(modelsStructure.SeriesGroup)
        .filter(
            modelsStructure.SeriesGroup.id == group_id,
            modelsStructure.SeriesGroup.series_id == series_id,
        )
        .first()
    )

    if not db_group:
        raise HTTPException(
            status_code=404, detail="Grupo no encontrado o no pertenece a esta serie"
        )

    db_chapter = modelsStructure.Chapter(
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
            db.add(
                modelsStructure.ChapterTranslation(
                    chapter_id=db_chapter.id, language=trans.language, title=trans.title
                )
            )
        db.commit()

    return db_chapter

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    Date, DateTime, Float, ForeignKey, Enum, UniqueConstraint, 
    Table, CheckConstraint
)
from sqlalchemy.orm import relationship
from dependencies import Base 

# ==========================================
# 1. ENUMS
# ==========================================

class MediaType(enum.Enum):
    ANIME = "anime"
    MANGA = "manga"
    NOVEL = "novel"
    JAV = "jav"
    DOUJIN = "doujin"

class WatchStatus(enum.Enum):
    PLANNED = "planned"
    WATCHING = "watching"
    COMPLETED = "completed"
    DROPPED = "dropped"
    PAUSED = "paused"

class GroupType(enum.Enum):
    SEASON = "season"
    VOLUME = "volume"
    PART = "part"
    ABSOLUTE = "absolute"

class SeriesStatus(enum.Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    HIATUS = "hiatus"

class ReleaseStatus(enum.Enum):
    FINISHED = "finished"
    RELEASING = "releasing"
    ANNOUNCED = "announced"
    UNRELEASED = "unreleased"

class ExternalSource(enum.Enum):
    MYANIMELIST = "myanimelist"
    ANILIST = "anilist"
    KITSU = "kitsu"
    MANGAUPDATES = "mangaupdates"
    DMM = "dmm"
    JAVLIBRARY = "javlibrary"

class StaffRole(enum.Enum):
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

class RelationType(enum.Enum):
    SEQUEL = "sequel"
    PREQUEL = "prequel"
    SPIN_OFF = "spin_off"
    PARODY = "parody"
    ADAPTATION = "adaptation"
    SIDE_STORY = "side_story"

# ==========================================
# 2. CORE & ASOCIACIONES
# ==========================================

# Tabla pivote para Series <-> Géneros (Muchos a Muchos)
series_genres = Table(
    'series_genres', Base.metadata,
    Column('series_id', Integer, ForeignKey('series.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False) # ej: "isekai", "ntr"
    
    translations = relationship("GenreTranslation", back_populates="genre", cascade="all, delete-orphan")
    series = relationship("Series", secondary=series_genres, back_populates="genres")

class Series(Base):
    __tablename__ = 'series'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(MediaType), nullable=False)
    
    # Vital para JAV (IPX-123) y Libros (ISBN)
    reference_code = Column(String(50), index=True) 
    
    status = Column(Enum(SeriesStatus), default=SeriesStatus.ONGOING)
    is_adult = Column(Boolean, default=False) # Filtro R18
    original_language = Column(String(5), default="ja")
    cover_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    genres = relationship("Genre", secondary=series_genres, back_populates="series")
    translations = relationship("SeriesTranslation", back_populates="series", cascade="all, delete-orphan")
    staff = relationship("SeriesStaff", back_populates="series", cascade="all, delete-orphan")
    groups = relationship("SeriesGroup", back_populates="series", cascade="all, delete-orphan")
    external_links = relationship("ExternalLink", back_populates="series", cascade="all, delete-orphan")
    
    # Relaciones de contexto definidas abajo en SeriesRelation

# ==========================================
# 3. STAFF & CAST
# ==========================================

class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    original_name = Column(String(255))
    birth_date = Column(Date)
    gender = Column(String(20))
    image_url = Column(Text)

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(StaffRole)) # studio, maker, circle...
    country = Column(String(50))

class SeriesStaff(Base):
    """Tabla polimórfica: Vincula Serie con Persona O Compañía"""
    __tablename__ = 'series_staff'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    person_id = Column(Integer, ForeignKey('people.id', ondelete='CASCADE'), nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)
    
    role = Column(Enum(StaffRole), nullable=False)
    role_detail = Column(String(100)) 

    series = relationship("Series", back_populates="staff")
    person = relationship("People")
    company = relationship("Company")

    __table_args__ = (
        UniqueConstraint('series_id', 'person_id', 'role', 'company_id', name='_series_staff_uc'),
        CheckConstraint(
            '(person_id IS NOT NULL) OR (company_id IS NOT NULL)',
            name='check_staff_has_entity'
        ),
    )

# ==========================================
# 4. ESTRUCTURA (Jerarquía)
# ==========================================

class SeriesGroup(Base):
    """Temporadas, Volúmenes o Partes"""
    __tablename__ = 'series_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(GroupType), nullable=False)
    order_number = Column(Float, nullable=False)
    
    title = Column(String(255))
    cover_url = Column(Text)
    status = Column(Enum(ReleaseStatus), default=ReleaseStatus.UNRELEASED)
    start_date = Column(Date)
    end_date = Column(Date)

    series = relationship("Series", back_populates="groups")
    chapters = relationship("Chapter", back_populates="group", cascade="all, delete-orphan")
    translations = relationship("GroupTranslation", back_populates="group", cascade="all, delete-orphan")
    external_links = relationship("ExternalLink", back_populates="group", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('series_id', 'type', 'order_number', name='_series_group_order_uc'),
    )

class Chapter(Base):
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=False)
    
    number_in_group = Column(Float, nullable=False)
    absolute_number = Column(Float, nullable=True)
    
    duration = Column(Integer)
    release_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("SeriesGroup", back_populates="chapters")
    translations = relationship("ChapterTranslation", back_populates="chapter", cascade="all, delete-orphan")

# ==========================================
# 5. LOCALIZACIÓN (I18N)
# ==========================================

class SeriesTranslation(Base):
    __tablename__ = 'series_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    series = relationship("Series", back_populates="translations")
    __table_args__ = (UniqueConstraint('series_id', 'language', name='_series_lang_uc'),)

class GroupTranslation(Base):
    __tablename__ = 'group_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    title = Column(String(255))
    description = Column(Text)

    group = relationship("SeriesGroup", back_populates="translations")
    __table_args__ = (UniqueConstraint('group_id', 'language', name='_group_lang_uc'),)

class GenreTranslation(Base):
    __tablename__ = 'genre_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    genre_id = Column(Integer, ForeignKey('genres.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    name = Column(String(100), nullable=False)

    genre = relationship("Genre", back_populates="translations")
    __table_args__ = (UniqueConstraint('genre_id', 'language', name='_genre_lang_uc'),)

class ChapterTranslation(Base):
    __tablename__ = 'chapter_translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False)
    language = Column(String(5), nullable=False)
    title = Column(String(255))

    chapter = relationship("Chapter", back_populates="translations")
    __table_args__ = (UniqueConstraint('chapter_id', 'language', name='_chapter_lang_uc'),)

# ==========================================
# 6. RELACIONES ENTRE SERIES
# ==========================================

class SeriesRelation(Base):
    __tablename__ = 'series_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    type = Column(Enum(RelationType), nullable=False)

    source = relationship("Series", foreign_keys=[source_id])
    target = relationship("Series", foreign_keys=[target_id])

    __table_args__ = (UniqueConstraint('source_id', 'target_id', name='_rel_source_target_uc'),)

# ==========================================
# 7. USUARIOS & PROGRESO
# ==========================================

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserLibrary(Base):
    __tablename__ = 'user_library'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=False)
    
    status = Column(Enum(WatchStatus), default=WatchStatus.PLANNED)
    score = Column(Integer)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    progress_details = relationship("UserProgress", back_populates="library_entry", cascade="all, delete-orphan")
    
    __table_args__ = (UniqueConstraint('user_id', 'series_id', name='_user_series_uc'),)

class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_library_id = Column(Integer, ForeignKey('user_library.id', ondelete='CASCADE'), nullable=False)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=False)
    
    chapters_read = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    last_read_at = Column(DateTime, default=datetime.utcnow)

    library_entry = relationship("UserLibrary", back_populates="progress_details")
    group = relationship("SeriesGroup")

    __table_args__ = (UniqueConstraint('user_library_id', 'group_id', name='_lib_group_uc'),)

# ==========================================
# 8. SYNC EXTERNO
# ==========================================

class ExternalLink(Base):
    __tablename__ = 'external_links'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Enum(ExternalSource), nullable=False)
    external_id = Column(String(50), nullable=False)
    url = Column(String(255))
    
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'), nullable=True)
    group_id = Column(Integer, ForeignKey('series_groups.id', ondelete='CASCADE'), nullable=True)
    
    last_synced_at = Column(DateTime)

    series = relationship("Series", back_populates="external_links")
    group = relationship("SeriesGroup", back_populates="external_links")

    __table_args__ = (
        UniqueConstraint('source', 'external_id', name='_source_extid_uc'),
        CheckConstraint(
            '(series_id IS NOT NULL) OR (group_id IS NOT NULL)',
            name='check_link_has_parent'
        ),
    )
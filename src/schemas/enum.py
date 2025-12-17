# src/schemas/enum.py
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
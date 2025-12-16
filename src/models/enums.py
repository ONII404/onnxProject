import enum

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

__all__ = [
    "MediaType", "WatchStatus", "GroupType", "SeriesStatus",
    "ReleaseStatus", "ExternalSource", "StaffRole", "RelationType"
]
from src.config.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .enums import ExternalSource

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

__all__ = ["ExternalLink"]
# src/models/staff.py
from src.config.db import Base
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Enum, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .enums import StaffRole

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
    type = Column(Enum(StaffRole))  # studio, maker, circle...
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

__all__ = ["People", "Company", "SeriesStaff"]
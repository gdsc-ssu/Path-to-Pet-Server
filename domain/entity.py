from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Float, JSON, ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class AnimalBreed(PyEnum):
    GOLDEN_RETRIEVER = 'GoldenRetriever'
    CHIHUAHUA = 'Chihuahua'
    GERMAN_SHEPHERD = 'GermanShepherd'
    BEAGLE = 'Beagle'
    BULLDOG = 'Bulldog'
    POODLE = 'Poodle'
    BRITISH_SHORTHAIR = 'BritishShorthair'
    AMERICAN_SHORTHAIR = 'AmericanShorthair'
    BENGAL = 'Bengal'
    SIAMESE = 'Siamese'
    PERSIAN = 'Persian'
    SCOTTISH_FOLD = 'ScottishFold'

class Animal(Base):
    __tablename__ = 'animals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    admission_date = Column(DateTime, nullable=False)
    breed = Column(Enum(AnimalBreed))
    gender = Column(String(1), CheckConstraint('gender IN ("M", "F")'))
    is_neutered = Column(Boolean)
    name = Column(String(255))
    shelter_location = Column(String(255))
    shelter_contact = Column(String(255))
    location = Column(String(255))
    notes = Column(String(2048))
    photo_url = Column(String(2048))
    is_adopted = Column(Boolean, default=False)
    is_dog = Column(Boolean, default=True)
    password = Column(String(255), nullable=False)

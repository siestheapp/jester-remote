from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Numeric, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Brand(Base):
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    default_unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    
    # Relationships
    default_unit = relationship("Unit")
    size_guides = relationship("SizeGuide", back_populates="brand")
    size_aliases = relationship("SizeAlias", back_populates="brand")

class Gender(Base):
    __tablename__ = 'genders'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    
    # Relationships
    categories = relationship("Category", back_populates="gender")
    fits = relationship("Fit", back_populates="gender")
    size_guides = relationship("SizeGuide", back_populates="gender")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    gender_id = Column(Integer, ForeignKey('genders.id'))
    
    # Relationships
    gender = relationship("Gender", back_populates="categories")
    subcategories = relationship("Subcategory", back_populates="category")
    size_guides = relationship("SizeGuide", back_populates="category")

class Subcategory(Base):
    __tablename__ = 'subcategories'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(Text, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="subcategories")
    size_guides = relationship("SizeGuide", back_populates="subcategory")

class Fit(Base):
    __tablename__ = 'fits'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    gender_id = Column(Integer, ForeignKey('genders.id'))
    description = Column(Text)
    
    # Relationships
    gender = relationship("Gender", back_populates="fits")

class Unit(Base):
    __tablename__ = 'units'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    
    # Relationships
    measurements = relationship("SizeGuideMeasurement", back_populates="unit")
    validation_rules = relationship("ValidationRule", back_populates="unit")

class MeasurementType(Base):
    __tablename__ = 'measurement_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    measurements = relationship("SizeGuideMeasurement", back_populates="measurement_type")
    validation_rules = relationship("ValidationRule", back_populates="measurement_type")

class SizeGuide(Base):
    __tablename__ = 'size_guides'
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    size_label = Column(Text, nullable=False)
    neck_min = Column(Numeric)
    neck_max = Column(Numeric)
    chest_min = Column(Numeric)
    chest_max = Column(Numeric)
    waist_min = Column(Numeric)
    waist_max = Column(Numeric)
    sleeve_min = Column(Numeric)
    sleeve_max = Column(Numeric)
    belt_min = Column(Numeric)
    belt_max = Column(Numeric)
    source_url = Column(Text)
    size_guide_header = Column(Text)
    scope = Column(Text)
    ingestion_uuid = Column(UUID)
    category_id = Column(Integer, ForeignKey('categories.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))
    gender_id = Column(Integer, ForeignKey('genders.id'))
    
    # Relationships
    brand = relationship("Brand", back_populates="size_guides")
    category = relationship("Category", back_populates="size_guides")
    subcategory = relationship("Subcategory", back_populates="size_guides")
    gender = relationship("Gender", back_populates="size_guides")
    measurements = relationship("SizeGuideMeasurement", back_populates="size_guide")

class SizeGuideMeasurement(Base):
    __tablename__ = 'size_guide_measurements'
    
    id = Column(Integer, primary_key=True)
    size_guide_id = Column(Integer, ForeignKey('size_guides.id'), nullable=False)
    measurement_type_id = Column(Integer, ForeignKey('measurement_types.id'), nullable=False)
    min_value = Column(Numeric)
    max_value = Column(Numeric)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    size_guide = relationship("SizeGuide", back_populates="measurements")
    measurement_type = relationship("MeasurementType", back_populates="measurements")
    unit = relationship("Unit", back_populates="measurements")

class ValidationRule(Base):
    __tablename__ = 'validation_rules'
    
    id = Column(Integer, primary_key=True)
    measurement_type_id = Column(Integer, ForeignKey('measurement_types.id'), nullable=False)
    min_allowed = Column(Numeric)
    max_allowed = Column(Numeric)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    measurement_type = relationship("MeasurementType", back_populates="validation_rules")
    unit = relationship("Unit", back_populates="validation_rules")

class SizeAlias(Base):
    __tablename__ = 'size_aliases'
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brands.id'))
    gender_id = Column(Integer, ForeignKey('genders.id'))
    size_label = Column(Text, nullable=False)
    mapped_size = Column(Text, nullable=False)
    
    # Relationships
    brand = relationship("Brand", back_populates="size_aliases")
    gender = relationship("Gender")

class IngestionLog(Base):
    __tablename__ = 'ingestion_log'
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey('brands.id'))
    category = Column(Text)
    filename = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_url = Column(Text)
    size_guide_header = Column(Text)
    scope = Column(Text)
    notes = Column(Text)
    ingestion_uuid = Column(UUID, default=uuid.uuid4)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=False)
    
    # Relationships
    brand = relationship("Brand")
    gender = relationship("Gender")

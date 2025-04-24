"""
Size Guide data models for the application.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class Measurement(BaseModel):
    """Individual measurement within a size guide."""
    name: str = Field(..., description="Name of the measurement (e.g., 'Chest', 'Waist')")
    value: float = Field(..., description="Numerical value of the measurement")
    unit: str = Field(..., description="Unit of measurement (e.g., 'inches', 'cm')")
    description: Optional[str] = Field(None, description="Additional details about the measurement")

class SizeGuide(BaseModel):
    """Core size guide data model."""
    id: Optional[str] = Field(None, description="Unique identifier for the size guide")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category (e.g., 'Shirts', 'Pants')")
    measurements: Dict[str, List[Measurement]] = Field(..., description="Size measurements by size name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata about the size guide")

    class Config:
        json_schema_extra = {
            "example": {
                "brand": "Example Brand",
                "category": "Shirts",
                "measurements": {
                    "S": [
                        {
                            "name": "Chest",
                            "value": 38.0,
                            "unit": "inches",
                            "description": "Measured across fullest part"
                        }
                    ]
                },
                "metadata": {
                    "fit_type": "Regular",
                    "gender": "Men's"
                }
            }
        } 
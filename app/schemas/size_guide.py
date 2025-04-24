"""
API schemas for size guide operations.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from app.models.size_guide import Measurement, SizeGuide

class SizeGuideCreateRequest(BaseModel):
    """Request schema for creating a new size guide."""
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category")
    image_data: str = Field(..., description="Base64 encoded image data")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")

class SizeGuideCreateResponse(BaseModel):
    """Response schema for size guide creation."""
    guide: SizeGuide
    extracted_data: Dict[str, List[Measurement]]
    message: str = Field(default="Size guide processed successfully")

class SizeGuideQueryRequest(BaseModel):
    """Request schema for querying size guides."""
    brand: Optional[str] = Field(None, description="Filter by brand")
    category: Optional[str] = Field(None, description="Filter by category")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Filter by metadata")

class SizeGuideQueryResponse(BaseModel):
    """Response schema for size guide queries."""
    guides: List[SizeGuide]
    total: int = Field(..., description="Total number of matching guides")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=10, description="Items per page") 
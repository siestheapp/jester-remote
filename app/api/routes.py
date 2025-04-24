"""
API routes for the Jester application.
This module defines all the API endpoints for the application.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

from app.core.vision import process_size_guide_image
from app.core.jester_chat import JesterChat
from app.core.vector_search import JesterVectorSearch
from app.config import config

# Create router
router = APIRouter(
    prefix="/api",
    tags=["jester"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
vector_search = JesterVectorSearch()
chat = JesterChat(vector_search)

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@router.post("/process-size-guide")
async def process_size_guide(
    file: UploadFile = File(...),
    brand: str = Form(...),
    gender: str = Form(...),
    size_guide_header: str = Form(...),
    source_url: str = Form(...),
    unit_of_measurement: str = Form(...),
    size_guide_scope: str = Form(...)
):
    """
    Process a size guide image and extract size information.
    
    Args:
        file: The uploaded size guide image
        brand: Brand name
        gender: Gender (men/women/unisex)
        size_guide_header: Header text from the size guide
        source_url: URL where the size guide was found
        unit_of_measurement: Unit of measurement used (cm/inches)
        size_guide_scope: Scope of the size guide (e.g., "US", "EU", "UK")
        
    Returns:
        dict: Extracted size information
    """
    try:
        # Ensure upload directory exists
        os.makedirs(config.UPLOADS_DIR, exist_ok=True)
        
        # Save the uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{brand}_{timestamp}_{file.filename}"
        file_path = os.path.join(config.UPLOADS_DIR, filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the image
        result = await process_size_guide_image(file_path)
        
        # Add metadata
        result["metadata"] = {
            "brand": brand,
            "gender": gender,
            "size_guide_header": size_guide_header,
            "source_url": source_url,
            "unit_of_measurement": unit_of_measurement,
            "size_guide_scope": size_guide_scope,
            "source_image": file_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to knowledge base
        vector_search.add_chunk(
            json.dumps(result),
            f"Size guide for {brand} {gender} clothing using {unit_of_measurement} measurements"
        )
        
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_endpoint(query: str):
    """
    Chat with Jester about size guides.
    
    Args:
        query: The user's query
        
    Returns:
        dict: Jester's response
    """
    try:
        response = chat.get_response(query)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

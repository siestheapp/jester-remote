"""
API routes for the Jester application.
This module defines all the API endpoints for the application.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime
from pathlib import Path

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
chat = JesterChat()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@router.post("/process-size-guide")
async def process_size_guide(
    file: UploadFile = File(...),
    brand: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    size_guide_header: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    unit_of_measurement: Optional[str] = Form(None),
    size_guide_scope: Optional[str] = Form(None)
):
    print("==== DEBUG: Request Received ====")
    print(f"Filename: {file.filename}")
    print(f"Content-Type: {file.content_type}")
    print(f"Brand: {brand}")
    print(f"Unit: {unit_of_measurement}")
    try:
        content = await file.read()
        print(f"File Size: {len(content)} bytes")
        file.file.seek(0)
    except Exception as e:
        print(f"Failed to read file: {e}")


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
        upload_dir = Path(config.UPLOADS_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / filename
        
        # Read the file content and write it
        content = await file.read()
        print(f"Received file: {file.filename}, size: {len(content)} bytes")  # Diagnostic: print file size
        with open(file_path, "wb") as f:
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
        # Get detailed error information
        import traceback
        error_details = traceback.format_exc()
        print(f"Exception in process_size_guide: {e}")
        print(f"Detailed error: {error_details}")
        print(f"File content type: {file.content_type}")
        print(f"File size: {len(content)} bytes")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "details": error_details,
                "file_info": {
                    "content_type": file.content_type,
                    "size_bytes": len(content)
                }
            }
        )

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

"""
Main application module for Jester.
This module initializes the FastAPI application and configures all necessary components.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import traceback

from app.api import router as api_router

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Jester API",
        description="API for processing size guides and providing size recommendations",
        version="1.0.0"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include application routes
    app.include_router(api_router)

    # Enhanced error handler to debug silent 400 errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        body = await request.body()
        print("❌ FASTAPI VALIDATION ERROR")
        print("Raw Request Body (first 500 bytes):", body[:500])
        print("Validation Errors:", exc.errors())
        print("Traceback:\n", traceback.format_exc())
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors()},
        )

    return app

# Create the FastAPI app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

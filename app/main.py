from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
import numpy as np
import cv2
from typing import Dict

from app.utils import get_model
from app.processing import extract_aadhaar_data
from app.models import AadhaarResponse


# Global variable to store the loaded model
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event to load the YOLO model at startup.
    This ensures the model is loaded once and reused across requests.
    """
    global model
    print("Loading YOLO model...")
    model = get_model()
    print("YOLO model loaded successfully!")
    yield
    # Cleanup (if needed)
    print("Shutting down application...")


# Initialize FastAPI application
app = FastAPI(
    title="Aadhaar Card Information Extraction API",
    description="Extract information from Aadhaar cards using YOLOv8 and Tesseract OCR",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Aadhaar Card Extraction API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/api/v1/extract/", response_model=AadhaarResponse)
async def extract_aadhaar_info(image: UploadFile = File(...)):
    """
    Extract information from an uploaded Aadhaar card image.
    
    Args:
        image: Uploaded image file (JPEG, PNG, etc.)
    
    Returns:
        AadhaarResponse: Extracted Aadhaar card information
    
    Raises:
        HTTPException: If image processing fails
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file."
        )
    
    try:
        # Read the uploaded file bytes
        image_bytes = await image.read()
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image using OpenCV
        image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_cv is None:
            raise HTTPException(
                status_code=422,
                detail="Unable to decode image. Please ensure the file is a valid image."
            )
        
        # Run processing in thread pool to avoid blocking the event loop
        extracted_data = await run_in_threadpool(
            extract_aadhaar_data,
            image_cv,
            model
        )
        
        return AadhaarResponse(**extracted_data)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing image: {str(e)}"
        )

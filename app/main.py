"""
Main FastAPI application for Aadhaar card data extraction.
"""
import os
import time
import uuid
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

from app.config import get_settings
from app.logger import logger
from app.models import (
    ExtractionResponse,
    ErrorResponse,
    HealthResponse,
    Detection,
    AadhaarData
)
from app.utils import (
    validate_file_extension,
    validate_file_size,
    cleanup_temp_file,
    check_tesseract_available,
    extract_text_from_region,
    postprocess_extracted_data,
    save_upload_file
)


# Global model variable
model: Optional[YOLO] = None
tesseract_available: bool = False


def load_yolo_model() -> YOLO:
    """
    Load YOLO model from HuggingFace Hub.
    
    Returns:
        Loaded YOLO model
    """
    settings = get_settings()
    model_path = Path(settings.MODEL_DIR) / settings.MODEL_FILENAME
    
    try:
        # Download model if not exists
        if not model_path.exists():
            logger.info(f"Downloading model from HuggingFace: {settings.MODEL_REPO_ID}")
            downloaded_path = hf_hub_download(
                repo_id=settings.MODEL_REPO_ID,
                filename=settings.MODEL_FILENAME,
                cache_dir=settings.MODEL_DIR
            )
            logger.info(f"Model downloaded to: {downloaded_path}")
            model_path = Path(downloaded_path)
        else:
            logger.info(f"Using existing model at: {model_path}")
        
        # Load model
        yolo_model = YOLO(str(model_path))
        logger.info("YOLO model loaded successfully")
        return yolo_model
        
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {str(e)}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    global model, tesseract_available
    
    # Startup
    logger.info("Starting up Aadhaar OCR application...")
    
    try:
        # Load YOLO model
        model = load_yolo_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {str(e)}")
        model = None
    
    # Check Tesseract availability
    tesseract_available = check_tesseract_available()
    if not tesseract_available:
        logger.warning("Tesseract OCR is not available")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Aadhaar OCR application...")


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title="Aadhaar Card OCR API",
    description="Extract data from Aadhaar card images using YOLOv8 and Tesseract OCR",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Aadhaar Card OCR API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return HealthResponse(
        status="healthy" if model is not None and tesseract_available else "degraded",
        model_loaded=model is not None,
        tesseract_available=tesseract_available,
        version="1.0.0"
    )


@app.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Extraction"]
)
async def extract_aadhaar_data(
    file: UploadFile = File(..., description="Aadhaar card image file (JPG, JPEG, PNG)")
):
    """
    Extract data from Aadhaar card image.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Extracted Aadhaar data with detections and processing time
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # Check if model is loaded
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not loaded. Please try again later."
            )
        
        # Check if Tesseract is available
        if not tesseract_available:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Tesseract OCR not available"
            )
        
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content to validate size
        file_content = await file.read()
        if not validate_file_size(len(file_content)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Save uploaded file temporarily
        temp_file_path = os.path.join(
            settings.UPLOAD_DIR,
            f"{uuid.uuid4()}_{file.filename}"
        )
        
        with open(temp_file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Processing file: {file.filename}")
        
        # Read image
        image = cv2.imread(temp_file_path)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read image. File may be corrupted."
            )
        
        # Run YOLO detection
        results = model(image, conf=settings.CONFIDENCE_THRESHOLD)
        
        # Only process these 4 fields
        REQUIRED_FIELDS = {'AADHAR_NUMBER', 'NAME', 'DATE_OF_BIRTH', 'GENDER'}
        
        # Process detections
        detections = []
        extracted_data = {}
        
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            
            for i in range(len(boxes)):
                # Get detection details
                box = boxes.xyxy[i].cpu().numpy()  # Bounding box
                conf = float(boxes.conf[i].cpu().numpy())  # Confidence
                cls = int(boxes.cls[i].cpu().numpy())  # Class ID
                
                # Get label name
                label = model.names[cls]
                
                # Skip fields we don't need
                if label not in REQUIRED_FIELDS:
                    continue
                
                # Extract text from region
                text = extract_text_from_region(image, box, label)
                
                # Store detection
                detection = Detection(
                    label=label,
                    confidence=conf,
                    bbox=box.tolist(),
                    text=text
                )
                detections.append(detection)
                
                # Store in extracted data with field mapping
                if text:
                    # Map DATE_OF_BIRTH to DOB for consistency
                    field_name = "DOB" if label == "DATE_OF_BIRTH" else label
                    extracted_data[field_name] = text
        
        # Post-process extracted data
        processed_data = postprocess_extracted_data(extracted_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = ExtractionResponse(
            success=True,
            data=AadhaarData(**processed_data) if processed_data else None,
            detections=detections,
            processing_time=round(processing_time, 3),
            message="Data extracted successfully" if processed_data else "No data detected"
        )
        
        logger.info(f"Processed {file.filename} in {processing_time:.3f}s. Found {len(detections)} detections.")
        
        return response
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        
    finally:
        # Cleanup temporary file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "detail": getattr(exc, "detail", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

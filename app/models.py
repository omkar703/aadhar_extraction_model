"""
Pydantic models for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")


class Detection(BaseModel):
    """Detection result from YOLO model."""
    label: str = Field(..., description="Detected field label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    bbox: List[float] = Field(..., description="Bounding box coordinates [x1, y1, x2, y2]")
    text: Optional[str] = Field(None, description="Extracted text from OCR")


class AadhaarData(BaseModel):
    """Extracted Aadhaar card data."""
    AADHAR_NUMBER: Optional[str] = Field(None, description="Aadhaar card number")
    NAME: Optional[str] = Field(None, description="Cardholder name")
    DOB: Optional[str] = Field(None, description="Date of birth")
    GENDER: Optional[str] = Field(None, description="Gender")
    
    class Config:
        json_schema_extra = {
            "example": {
                "AADHAR_NUMBER": "1234 5678 9012",
                "NAME": "John Doe",
                "DOB": "01/01/1990",
                "GENDER": "Male",
                "ADDRESS": "123 Street, City, State - 123456"
            }
        }


class ExtractionResponse(BaseModel):
    """Response model for Aadhaar data extraction."""
    success: bool = Field(..., description="Whether extraction was successful")
    data: Optional[AadhaarData] = Field(None, description="Extracted Aadhaar data")
    detections: List[Detection] = Field(default_factory=list, description="All detections with OCR results")
    processing_time: float = Field(..., description="Processing time in seconds")
    message: Optional[str] = Field(None, description="Additional message or error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "AADHAR_NUMBER": "1234 5678 9012",
                    "NAME": "John Doe",
                    "DOB": "01/01/1990",
                    "GENDER": "Male",
                    "ADDRESS": "123 Street, City, State - 123456"
                },
                "detections": [
                    {
                        "label": "AADHAR_NUMBER",
                        "confidence": 0.95,
                        "bbox": [100, 200, 300, 250],
                        "text": "1234 5678 9012"
                    }
                ],
                "processing_time": 1.23
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid file format",
                "detail": "Only JPG, JPEG, and PNG formats are supported"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether YOLO model is loaded")
    tesseract_available: bool = Field(..., description="Whether Tesseract is available")
    version: str = Field("1.0.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "tesseract_available": True,
                "version": "1.0.0"
            }
        }

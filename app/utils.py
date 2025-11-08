"""
Utility functions for image processing, OCR, and validation.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np
import pytesseract
from PIL import Image
from app.config import get_settings
from app.logger import logger


def validate_file_extension(filename: str) -> bool:
    """
    Validate if the file has an allowed extension.
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        True if extension is allowed, False otherwise
    """
    settings = get_settings()
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    Validate if the file size is within the allowed limit.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if size is valid, False otherwise
    """
    settings = get_settings()
    return file_size <= settings.max_file_size_bytes


def cleanup_temp_file(file_path: str) -> None:
    """
    Safely delete a temporary file.
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {file_path}: {str(e)}")


def check_tesseract_available() -> bool:
    """
    Check if Tesseract OCR is available.
    
    Returns:
        True if Tesseract is available, False otherwise
    """
    settings = get_settings()
    try:
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract not available: {str(e)}")
        return False


def preprocess_image(image: np.ndarray, enhance: bool = True) -> np.ndarray:
    """
    Preprocess image for better OCR results.
    
    Args:
        image: Input image as numpy array
        enhance: Whether to apply additional enhancement
        
    Returns:
        Preprocessed image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    if enhance:
        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Upscale image for better OCR
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh


def extract_text_from_region(
    image: np.ndarray, 
    bbox: Tuple[int, int, int, int],
    label: str
) -> str:
    """
    Extract text from a specific region of the image using OCR.
    
    Args:
        image: Input image as numpy array
        bbox: Bounding box coordinates (x1, y1, x2, y2)
        label: Label of the detected field
        
    Returns:
        Extracted text
    """
    try:
        x1, y1, x2, y2 = map(int, bbox)
        
        # Extract region with no padding initially
        h, w = image.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        
        # Extract region
        crop = image[y1:y2, x1:x2]
        
        if crop.size == 0:
            logger.warning(f"Empty region for {label}")
            return ""
        
        # Convert BGR to RGB then to grayscale
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        crop_pil = Image.fromarray(crop_rgb)
        crop_pil = crop_pil.convert('L')  # Convert to grayscale
        
        # Use PSM 7 (single line) - works best for Aadhaar cards
        ocr_config = r'--oem 3 --psm 7 -l eng'
        
        # Perform OCR
        text = pytesseract.image_to_string(crop_pil, config=ocr_config)
        
        # Clean up text - remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.debug(f"Extracted text for {label}: '{text}'")
        return text if text else None
        
    except Exception as e:
        logger.error(f"Error extracting text from region for {label}: {str(e)}")
        return ""
        # Perform OCR
        text = pytesseract.image_to_string(
            pil_image,
            config=ocr_config
        )
        
        # Clean up text
        text = text.strip()
        text = ' '.join(text.split())  # Normalize whitespace
        
        logger.debug(f"Extracted text for {label}: {text}")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from region for {label}: {str(e)}")
        return ""


def clean_aadhaar_number(text: str) -> str:
    """
    Clean and format Aadhaar number.
    
    Args:
        text: Raw text containing Aadhaar number
        
    Returns:
        Cleaned Aadhaar number
    """
    # Extract only digits
    digits = re.sub(r'\D', '', text)
    
    # Aadhaar number should be 12 digits
    if len(digits) == 12:
        # Format as XXXX XXXX XXXX
        return f"{digits[0:4]} {digits[4:8]} {digits[8:12]}"
    elif len(digits) > 12:
        # Take first 12 digits
        digits = digits[:12]
        return f"{digits[0:4]} {digits[4:8]} {digits[8:12]}"
    
    return text


def clean_date(text: str) -> str:
    """
    Clean and format date string.
    
    Args:
        text: Raw text containing date
        
    Returns:
        Cleaned date string
    """
    if not text:
        return None
        
    # Remove any non-date characters
    text = re.sub(r'[^0-9/\-]', '', text)
    
    # Common date patterns
    patterns = [
        r'(\d{2})[/-](\d{2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{2})[/-](\d{2})[/-](\d{2})',   # DD/MM/YY or DD-MM-YY
        r'(\d{4})',  # Just year (YYYY)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            matched_text = match.group(0).replace('-', '/')
            # If it's just a year, return as is
            if len(matched_text) == 4 and matched_text.isdigit():
                return matched_text
            return matched_text
    
    # If no pattern matched but we have digits, return them
    # This handles cases where OCR only captures partial dates
    return text if text else None


def clean_name(text: str) -> str:
    """
    Clean and format name text.
    
    Args:
        text: Raw text containing name
        
    Returns:
        Cleaned name string
    """
    # Remove excessive punctuation and special characters
    # Keep only letters, spaces, apostrophes, and basic punctuation
    text = re.sub(r'[^a-zA-Z\s\'\-\.]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove trailing punctuation
    text = text.rstrip('.,\'-')
    
    # Capitalize properly
    text = text.title()
    
    return text


def clean_gender(text: str) -> Optional[str]:
    """
    Clean and standardize gender text.
    
    Args:
        text: Raw text containing gender
        
    Returns:
        Standardized gender string or None
    """
    # Remove special characters and extra whitespace
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.strip().lower()
    
    # Try to match common patterns
    if 'male' in text and 'female' not in text:
        return "Male"
    elif 'female' in text or 'femal' in text:
        return "Female"
    elif text in ['m', 'man']:
        return "Male"
    elif text in ['f', 'woman']:
        return "Female"
    
    return text if text else None


def postprocess_extracted_data(data: dict) -> dict:
    """
    Post-process extracted data to clean and format it.
    Only processes: AADHAR_NUMBER, NAME, DOB, GENDER
    
    Args:
        data: Dictionary of extracted data
        
    Returns:
        Cleaned and formatted data dictionary
    """
    processed = {
        "AADHAR_NUMBER": None,
        "NAME": None,
        "DOB": None,
        "GENDER": None
    }
    
    for key, value in data.items():
        if not value:
            continue
            
        if key == "AADHAR_NUMBER":
            processed[key] = clean_aadhaar_number(value)
        elif key == "DOB":
            processed[key] = clean_date(value)
        elif key == "GENDER":
            processed[key] = clean_gender(value)
        elif key == "NAME":
            processed[key] = clean_name(value)
    
    return processed


def save_upload_file(upload_file, destination: str) -> None:
    """
    Save uploaded file to destination.
    
    Args:
        upload_file: FastAPI UploadFile object
        destination: Destination file path
    """
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.debug(f"Saved uploaded file to: {destination}")
    finally:
        upload_file.file.close()

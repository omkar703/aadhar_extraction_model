import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
from typing import Dict
from ultralytics import YOLO


def extract_aadhaar_data(image_cv: np.ndarray, model: YOLO) -> Dict[str, str]:
    """
    Extract Aadhaar card information from an image using YOLO detection and Tesseract OCR.
    
    Args:
        image_cv: OpenCV image as numpy array (BGR format)
        model: Pre-loaded YOLOv8 model
    
    Returns:
        Dictionary mapping field labels to extracted text values
    """
    # Store extracted information
    extracted_info = {}
    
    # Run YOLO detection on the image
    results = model(image_cv, conf=0.5)
    
    # Process each detection result
    for result in results:
        # Get the boxes from the result
        boxes = result.boxes
        
        if boxes is None or len(boxes) == 0:
            continue
        
        # Iterate through each detected box
        for box in boxes:
            # Get confidence score
            confidence = float(box.conf[0])
            
            # Filter by confidence threshold
            if confidence < 0.5:
                continue
            
            # Get class label
            class_id = int(box.cls[0])
            label = model.names[class_id]
            
            # Get bounding box coordinates [x1, y1, x2, y2]
            bbox = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = bbox
            
            # Ensure coordinates are within image bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image_cv.shape[1], x2)
            y2 = min(image_cv.shape[0], y2)
            
            # Crop the detected region from the image
            cropped_region = image_cv[y1:y2, x1:x2]
            
            if cropped_region.size == 0:
                continue
            
            # Convert cropped OpenCV image (BGR) to PIL Image (RGB)
            cropped_rgb = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cropped_rgb)
            
            # Preprocess for OCR: convert to grayscale
            pil_image_gray = pil_image.convert('L')
            
            # Run Tesseract OCR
            ocr_config = r'--oem 3 --psm 7 -l eng'
            extracted_text = pytesseract.image_to_string(pil_image_gray, config=ocr_config)
            
            # Clean the extracted text
            cleaned_text = extracted_text.strip()
            # Replace multiple spaces with single space
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Store in dictionary (use the latest detection if multiple exist)
            if cleaned_text:
                extracted_info[label] = cleaned_text
            else:
                extracted_info[label] = None
    
    # Special formatting for AADHAR_NUMBER
    if 'AADHAR_NUMBER' in extracted_info and extracted_info['AADHAR_NUMBER']:
        aadhar_text = extracted_info['AADHAR_NUMBER']
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', aadhar_text)
        
        # If exactly 12 digits, format as XXXX XXXX XXXX
        if len(digits_only) == 12:
            formatted_aadhar = f"{digits_only[0:4]} {digits_only[4:8]} {digits_only[8:12]}"
            extracted_info['AADHAR_NUMBER'] = formatted_aadhar
        else:
            # Keep original if not 12 digits
            extracted_info['AADHAR_NUMBER'] = digits_only if digits_only else None
    
    return extracted_info

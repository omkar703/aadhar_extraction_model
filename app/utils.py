from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import os


# Singleton pattern for model loading
_model = None


def get_model():
    """
    Load the YOLOv8 model from Hugging Face Hub.
    Uses a singleton pattern to ensure the model is loaded only once.
    
    Returns:
        YOLO: Loaded YOLOv8 model instance
    """
    global _model
    
    if _model is not None:
        return _model
    
    # Download model from Hugging Face Hub
    # This will cache the model locally if it doesn't exist
    model_path = hf_hub_download(
        repo_id="arnabdhar/YOLOv8-nano-aadhar-card",
        filename="model.pt"
    )
    
    print(f"Model downloaded to: {model_path}")
    
    # Load the YOLO model
    _model = YOLO(model_path)
    
    print(f"Model loaded with classes: {_model.names}")
    
    return _model

#!/bin/bash

set -e  # Exit on error

echo "================================================"
echo "Aadhaar Card Extraction API - Setup & Start"
echo "================================================"

# Check if running as root for system packages
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else 
    SUDO="sudo"
fi

# Step 1: Install system dependencies
echo "\n[1/5] Checking system dependencies..."
if ! command -v tesseract &> /dev/null; then
    echo "Installing Tesseract OCR..."
    $SUDO apt-get update
    $SUDO apt-get install -y tesseract-ocr libtesseract-dev libgl1-mesa-glx libglib2.0-0
else
    echo "✓ Tesseract OCR already installed"
fi

# Step 2: Check Python version
echo "\n[2/5] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# Step 3: Create virtual environment if it doesn't exist
echo "\n[3/5] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Step 4: Install Python dependencies
echo "\n[4/5] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✓ Dependencies installed successfully"
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Step 5: Download YOLO model from Hugging Face
echo "\n[5/5] Downloading YOLOv8 model from Hugging Face..."
python3 -c "from huggingface_hub import hf_hub_download; print('Downloading model...'); hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt'); print('✓ Model downloaded successfully')"

echo "\n================================================"
echo "Setup Complete! Starting API Server..."
echo "================================================\n"

# Start the FastAPI application
echo "Starting uvicorn server..."
echo "API will be available at: http://0.0.0.0:${PORT:-8000}"
echo "API Documentation at: http://0.0.0.0:${PORT:-8000}/docs"
echo "\nPress Ctrl+C to stop the server\n"

uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2} --reload

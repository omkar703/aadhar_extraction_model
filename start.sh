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
echo "\n[1/6] Checking system dependencies..."
if ! command -v tesseract &> /dev/null; then
    echo "Installing Tesseract OCR and required libraries..."
    $SUDO apt-get update
    $SUDO apt-get install -y tesseract-ocr libtesseract-dev libgl1-mesa-glx libglib2.0-0 python3-venv python3-pip

else
    echo "✓ Tesseract OCR already installed"
fi

# Ensure python3-venv is installed (required for EC2 Ubuntu/Debian instances)
if ! dpkg -l | grep -q python3-venv; then
    echo "Installing python3-venv..."
    $SUDO apt-get install -y python3-venv python3-pip
fi

# Step 2: Check Python version
echo "\n[2/6] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# Step 3: Create virtual environment if it doesn't exist
echo "\n[3/6] Setting up Python virtual environment..."
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "Creating virtual environment..."
    rm -rf venv  # Remove if corrupted
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated: $VIRTUAL_ENV"

# Step 4: Install Python dependencies
echo "\n[4/6] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Upgrading pip..."
    pip install --upgrade pip --no-cache-dir
    
    echo "Installing packages from requirements.txt..."
    # Use --no-cache-dir to save disk space on EC2
    pip install -r requirements.txt --no-cache-dir
    echo "✓ Dependencies installed successfully"
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Step 5: Verify app structure
echo "\n[5/6] Verifying application structure..."
if [ ! -d "app" ]; then
    echo "Error: app directory not found!"
    exit 1
fi

if [ ! -f "app/main.py" ]; then
    echo "Error: app/main.py not found!"
    exit 1
fi
echo "✓ Application structure verified"

# Step 6: Pre-download YOLO model from Hugging Face
echo "\n[6/6] Downloading YOLOv8 model from Hugging Face..."
python3 << 'PYTHON_SCRIPT'
import sys
try:
    from huggingface_hub import hf_hub_download
    print('Downloading model from Hugging Face...')
    model_path = hf_hub_download(
        repo_id='arnabdhar/YOLOv8-nano-aadhar-card',
        filename='model.pt'
    )
    print(f'✓ Model downloaded successfully to: {model_path}')
except Exception as e:
    print(f'Warning: Failed to pre-download model: {e}')
    print('Model will be downloaded on first API request.')
    sys.exit(0)  # Don't fail the script
PYTHON_SCRIPT

echo "\n================================================"
echo "Setup Complete! Starting API Server..."
echo "================================================\n"

# Determine optimal worker count for EC2 instance
# Default to 2, but can be overridden via WORKERS env variable
WORKERS=${WORKERS:-2}

# For production, disable --reload
RELOAD_FLAG=""
if [ "${ENVIRONMENT:-production}" = "development" ]; then
    RELOAD_FLAG="--reload"
    echo "Running in development mode with auto-reload enabled"
fi

# Start the FastAPI application
echo "Starting uvicorn server..."
echo "Workers: $WORKERS"
echo "Port: ${PORT:-8000}"
echo "API will be available at: http://0.0.0.0:${PORT:-8000}"
echo "API Documentation at: http://0.0.0.0:${PORT:-8000}/docs"
echo "Health check at: http://0.0.0.0:${PORT:-8000}/"
echo "\nPress Ctrl+C to stop the server\n"

# Use exec to replace shell with uvicorn process (better for signal handling)
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers $WORKERS $RELOAD_FLAG

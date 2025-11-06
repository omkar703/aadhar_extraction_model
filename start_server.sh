#!/bin/bash

set -e  # Exit on error

# Parse command line arguments
MODE=${1:-foreground}  # foreground or daemon
PORT=${PORT:-8000}
WORKERS=${WORKERS:-2}

echo "================================================"
echo "Aadhaar Card Extraction API - Server Setup"
echo "================================================"

# Check if running as root for system packages
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else 
    SUDO="sudo"
fi

# Step 1: Install system dependencies
echo ""
echo "[1/5] Checking system dependencies..."
if ! command -v tesseract &> /dev/null; then
    echo "Installing Tesseract OCR..."
    $SUDO apt-get update
    $SUDO apt-get install -y tesseract-ocr libtesseract-dev libgl1 libglib2.0-0
else
    echo "✓ Tesseract OCR already installed"
fi

# Step 2: Check Python version
echo ""
echo "[2/5] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# Step 3: Create virtual environment if it doesn't exist
echo ""
echo "[3/5] Setting up Python virtual environment..."
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
echo ""
echo "[4/5] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo "✓ Dependencies installed successfully"
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Step 5: Download YOLO model from Hugging Face
echo ""
echo "[5/5] Downloading YOLOv8 model from Hugging Face..."
python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt')" 2>/dev/null || echo "Model already downloaded"
echo "✓ Model ready"

echo ""
echo "================================================"
echo "Setup Complete! Starting API Server..."
echo "================================================"
echo ""

# Start the application based on mode
if [ "$MODE" = "daemon" ]; then
    echo "Starting server in daemon mode..."
    echo "Port: $PORT"
    echo "Workers: $WORKERS"
    echo ""
    
    # Kill any existing uvicorn processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    
    # Start in background with nohup
    nohup uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers $WORKERS \
        > server.log 2>&1 &
    
    PID=$!
    echo $PID > server.pid
    
    # Wait a moment and check if it started
    sleep 2
    if ps -p $PID > /dev/null; then
        echo "✓ Server started successfully (PID: $PID)"
        echo ""
        echo "API available at: http://0.0.0.0:$PORT"
        echo "API Documentation: http://0.0.0.0:$PORT/docs"
        echo ""
        echo "View logs: tail -f server.log"
        echo "Stop server: kill $PID  (or: ./stop_server.sh)"
    else
        echo "✗ Server failed to start. Check server.log for details."
        exit 1
    fi
else
    echo "Starting server in foreground mode..."
    echo "Port: $PORT"
    echo "Workers: $WORKERS"
    echo ""
    echo "API will be available at: http://0.0.0.0:$PORT"
    echo "API Documentation: http://0.0.0.0:$PORT/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers $WORKERS \
        --reload
fi

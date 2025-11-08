#!/bin/bash
set -e

echo "========================================="
echo "Aadhaar Card OCR API - Starting Up"
echo "========================================="

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "No .env file found. Using default configuration..."
fi

# Set default values if not set
export MODEL_REPO_ID=${MODEL_REPO_ID:-"arnabdhar/YOLOv8-nano-aadhar-card"}
export MODEL_FILENAME=${MODEL_FILENAME:-"model.pt"}
export MODEL_DIR=${MODEL_DIR:-"./models"}
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}
export UPLOAD_DIR=${UPLOAD_DIR:-"/tmp/uploads"}

echo ""
echo "Configuration:"
echo "  Model Repo: $MODEL_REPO_ID"
echo "  Model File: $MODEL_FILENAME"
echo "  Model Dir: $MODEL_DIR"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Log Level: $LOG_LEVEL"
echo ""

# Create necessary directories
echo "Creating required directories..."
mkdir -p "$MODEL_DIR"
mkdir -p "$UPLOAD_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Tesseract is available
if ! command -v tesseract &> /dev/null; then
    echo "Warning: Tesseract OCR is not installed or not in PATH"
    echo "Please install tesseract-ocr for OCR functionality"
else
    echo "Tesseract OCR found: $(tesseract --version | head -n 1)"
fi

echo ""
echo "Checking Python dependencies..."

# Check if required packages are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Error: Required Python packages not found"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

echo "Dependencies check passed!"
echo ""

# Download model if not exists
MODEL_PATH="$MODEL_DIR/$MODEL_FILENAME"
if [ ! -f "$MODEL_PATH" ]; then
    echo "Model file not found at $MODEL_PATH"
    echo "Model will be downloaded from HuggingFace on first startup..."
fi

echo ""
echo "========================================="
echo "Starting Uvicorn Server..."
echo "========================================="
echo ""

# Trap SIGTERM and SIGINT for graceful shutdown
trap 'echo "Shutting down gracefully..."; kill -TERM $PID; wait $PID' SIGTERM SIGINT

# Start Uvicorn server
if [ "$WORKERS" -gt 1 ] && [ "$RELOAD" != "True" ]; then
    # Production mode with multiple workers
    uvicorn app.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS" \
        --log-level "${LOG_LEVEL,,}" &
    PID=$!
else
    # Development mode or single worker
    uvicorn app.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --log-level "${LOG_LEVEL,,}" &
    PID=$!
fi

# Wait for the process
wait $PID

echo ""
echo "Application stopped."

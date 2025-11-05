# Aadhaar Card Information Extraction API

Production-ready FastAPI application for extracting information from Aadhaar cards using YOLOv8 object detection and Tesseract OCR.

## Features

- 🚀 **High Performance**: Pre-loaded model with async request handling
- 🐳 **Containerized**: Docker-ready with optimized image
- 🔍 **Accurate Detection**: YOLOv8-nano model trained on Aadhaar cards
- 📝 **OCR Extraction**: Tesseract-based text extraction
- ✅ **Production-Ready**: Error handling, validation, and proper logging
- 🔧 **Configurable**: Environment-based configuration

## Project Structure

```
aadhar_extraction_model/
├── app/
│   ├── main.py           # FastAPI app and endpoints
│   ├── processing.py     # YOLO detection & OCR logic
│   ├── models.py         # Pydantic models
│   └── utils.py          # Model loading singleton
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── start.sh             # Server startup script
├── .dockerignore        # Docker build exclusions
└── README.md            # This file
```

## Quick Start

### Local Development

1. **Install system dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr libtesseract-dev
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t aadhaar-extractor:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name aadhaar-api \
     -p 8000:8000 \
     -e WORKERS=4 \
     aadhaar-extractor:latest
   ```

3. **Check logs**:
   ```bash
   docker logs -f aadhaar-api
   ```

## API Usage

### Extract Aadhaar Information

**Endpoint**: `POST /api/v1/extract/`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/extract/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/aadhaar_card.jpg"
```

**Response**:
```json
{
  "AADHAR_NUMBER": "1234 5678 9012",
  "NAME": "John Doe",
  "ADDRESS": "123 Main Street, City, State - 123456",
  "DOB": "01/01/1990",
  "GENDER": "Male",
  "VID": null,
  "FATHER_NAME": null,
  "PHONE_NUMBER": null
}
```

### Health Check

**Endpoint**: `GET /`

```bash
curl http://localhost:8000/
```

## Configuration

Environment variables:

- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: 2)

## Model Information

- **Model**: YOLOv8-nano trained on Aadhaar cards
- **Source**: Hugging Face Hub (arnabdhar/YOLOv8-nano-aadhar-card)
- **Classes**: AADHAR_NUMBER, NAME, ADDRESS, DOB, GENDER, VID, etc.
- **Confidence Threshold**: 0.5

## OCR Configuration

- **Engine**: Tesseract OCR
- **Mode**: OEM 3 (default OCR Engine Mode)
- **PSM**: 7 (single text line)
- **Language**: English

## Performance Tips

1. **Workers**: Increase `WORKERS` for better throughput (recommend 2-4 per CPU core)
2. **Model Caching**: Model is pre-downloaded during Docker build
3. **Async Processing**: Uses thread pool for blocking I/O operations

## Troubleshooting

### Tesseract not found
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Model download issues
The model is automatically downloaded from Hugging Face Hub. Ensure you have internet connectivity during first run or Docker build.

### Memory issues
If running out of memory, reduce the number of workers:
```bash
docker run -e WORKERS=1 aadhaar-extractor:latest
```

## License

This project is provided as-is for educational and development purposes.

## Acknowledgments

- YOLOv8 model by arnabdhar on Hugging Face
- Ultralytics YOLOv8 framework
- Tesseract OCR engine

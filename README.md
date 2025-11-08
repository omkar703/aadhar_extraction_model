# Aadhaar Card OCR API

Production-ready FastAPI application for extracting data from Aadhaar card images using YOLOv8 object detection and Tesseract OCR.

## Features

- **YOLOv8 Object Detection**: Automatically detects fields on Aadhaar cards
- **Tesseract OCR**: Extracts text from detected regions
- **Production-Ready**: Includes Docker support, logging, error handling, and validation
- **RESTful API**: Clean and documented API endpoints
- **Async Operations**: Built with FastAPI for high performance
- **CORS Support**: Cross-origin requests enabled
- **Health Checks**: Built-in health monitoring
- **Input Validation**: File type and size validation
- **Memory Management**: Automatic cleanup of temporary files

## Supported Fields

- Aadhaar Number
- Name
- Date of Birth (DOB)
- Gender
- Address
- Father's Name
- Mother's Name
- Spouse's Name

## Requirements

- Python 3.10+
- Tesseract OCR
- Docker (optional, for containerized deployment)

## Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Clone or navigate to the project directory**:
   ```bash
   cd aadhar_project
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Local Deployment

1. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr libtesseract-dev libgl1-mesa-glx
   
   # macOS
   brew install tesseract
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the application**:
   ```bash
   ./start.sh
   ```
   
   Or directly with Python:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## API Usage

### POST /extract

Extract data from an Aadhaar card image.

**Request**:
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@aadhaar_card.jpg"
```

**Response**:
```json
{
  "success": true,
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
```

### GET /health

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "tesseract_available": true,
  "version": "1.0.0"
}
```

### GET /

Get API information.

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and modify as needed:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_REPO_ID` | `arnabdhar/YOLOv8-nano-aadhar-card` | HuggingFace model repository |
| `MODEL_FILENAME` | `model.pt` | Model file name |
| `MODEL_DIR` | `./models` | Directory to store model |
| `CONFIDENCE_THRESHOLD` | `0.5` | Detection confidence threshold |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size (MB) |
| `UPLOAD_DIR` | `/tmp/uploads` | Temporary upload directory |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `WORKERS` | `4` | Number of worker processes |
| `LOG_LEVEL` | `INFO` | Logging level |

## Docker Configuration

### Building the Docker Image

```bash
docker build -t aadhar-ocr-api .
```

### Running the Docker Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  --name aadhar-ocr \
  aadhar-ocr-api
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## Project Structure

```
aadhar_project/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging setup
│   ├── models.py            # Pydantic models
│   └── utils.py             # Utility functions
├── models/                  # YOLO model storage (auto-created)
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore           # Docker ignore rules
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── start.sh                # Startup script
└── README.md               # This file
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

### Security Considerations

1. **Change CORS settings** in `.env`:
   ```env
   CORS_ORIGINS=https://yourdomain.com
   ```

2. **Run as non-root user** (already configured in Docker)

3. **Use HTTPS** with a reverse proxy (nginx, traefik, etc.)

4. **Set up rate limiting** at the reverse proxy level

5. **Monitor logs** and set up alerts

### Scaling

To scale the application:

1. **Increase workers**:
   ```env
   WORKERS=8
   ```

2. **Deploy multiple containers** behind a load balancer:
   ```bash
   docker-compose up --scale aadhar-ocr-api=3
   ```

3. **Use Kubernetes** for orchestration (create k8s manifests as needed)

### Monitoring

- Monitor `/health` endpoint for service health
- Check logs: `docker-compose logs -f`
- Set up application performance monitoring (APM) tools

## Troubleshooting

### Model Download Issues

If the model fails to download:
```bash
# Manually download the model
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt', cache_dir='./models')"
```

### Tesseract Not Found

Ensure Tesseract is installed and in PATH:
```bash
tesseract --version
```

### Permission Denied

Make sure start.sh is executable:
```bash
chmod +x start.sh
```

### Out of Memory

Reduce the number of workers or increase container memory:
```yaml
# docker-compose.yml
services:
  aadhar-ocr-api:
    mem_limit: 4g
```

## Performance

- **First request**: ~2-5 seconds (model loading)
- **Subsequent requests**: ~1-2 seconds per image
- **Throughput**: ~30-50 requests/minute (depending on hardware)

## Development

### Running in Development Mode

```bash
# Enable auto-reload
export RELOAD=True
./start.sh
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (if test suite exists)
pytest
```

## License

This project is provided as-is for educational and development purposes.

## Credits

- **YOLOv8 Model**: [arnabdhar/YOLOv8-nano-aadhar-card](https://huggingface.co/arnabdhar/YOLOv8-nano-aadhar-card)
- **FastAPI**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Tesseract OCR**: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
- **Ultralytics**: [https://github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check application logs
4. Verify configuration in `.env`

## Version

**v1.0.0** - Initial production release

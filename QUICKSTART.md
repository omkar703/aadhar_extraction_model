# Quick Start Guide

Get the Aadhaar Card OCR API running in 5 minutes!

## 🚀 Fastest Way: Docker Compose

```bash
# Navigate to project directory
cd aadhar_project

# Start the API (builds and runs automatically)
docker-compose up --build

# API is now running at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

That's it! The API is ready to use.

## 📝 Test the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Extract data from an Aadhaar card
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_aadhaar_image.jpg"
```

### Using Python

```python
import requests

# Upload and extract data
url = "http://localhost:8000/extract"
files = {"file": open("aadhaar_card.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using Swagger UI

Open your browser and go to: `http://localhost:8000/docs`

Click on "POST /extract" → "Try it out" → Upload your image → Execute

## 🛠️ Without Docker (Local Installation)

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev libgl1-mesa-glx

# Install Python dependencies
pip install -r requirements.txt

# Run the application
./start.sh
```

## 🔧 Configuration

Create a `.env` file (optional):
```bash
cp .env.example .env
```

Edit `.env` to customize settings:
- `CONFIDENCE_THRESHOLD=0.5` - Detection confidence (0.0-1.0)
- `MAX_FILE_SIZE_MB=10` - Maximum upload size
- `WORKERS=4` - Number of worker processes
- `LOG_LEVEL=INFO` - Logging level

## 🎯 What Happens on First Run?

1. ✅ System dependencies are checked
2. ✅ YOLO model is downloaded from HuggingFace (~6MB)
3. ✅ Tesseract OCR is initialized
4. ✅ API server starts on port 8000

**First startup takes ~1-2 minutes** due to model download.

## 📊 Expected Response Format

```json
{
  "success": true,
  "data": {
    "AADHAR_NUMBER": "1234 5678 9012",
    "NAME": "John Doe",
    "DOB": "01/01/1990",
    "GENDER": "Male",
    "ADDRESS": "123 Street, City - 123456"
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

## 🐛 Common Issues

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Permission Denied on start.sh
```bash
chmod +x start.sh
```

### Model Download Fails
Check your internet connection. The model will auto-download on startup.

## 🔍 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop the API
docker-compose down

# Restart with fresh build
docker-compose up --build --force-recreate

# Run in background
docker-compose up -d
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Visit `/docs` for interactive API documentation
- Check `/health` endpoint for system status
- Review `app/config.py` for all configuration options

## 💡 Production Deployment

For production use:

1. Set proper CORS origins in `.env`
2. Use HTTPS (nginx/traefik reverse proxy)
3. Increase workers for better performance
4. Set up monitoring and alerts
5. Implement rate limiting

See [README.md](README.md) for detailed production deployment guide.

---

**Need Help?** Check the troubleshooting section in README.md

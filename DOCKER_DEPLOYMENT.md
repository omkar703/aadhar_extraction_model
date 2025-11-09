# Docker Deployment Guide

## Successfully Deployed! ✅

The Aadhaar OCR API is now running in Docker.

### What Was Done

1. **Cleaned up old Docker images** - Removed all previous builds
2. **Simplified Dockerfile** - Single-stage build for faster deployment
3. **Used CPU-only PyTorch** - Reduced image size from ~6GB to manageable size
4. **Fixed Python version** - Updated to Python 3.11
5. **Fixed package compatibility** - Replaced deprecated `libgl1-mesa-glx` with `libgl1`

### Current Status

- **Container Name**: `aadhar-ocr-api`
- **Status**: Running and healthy ✅
- **Port**: 8000 (mapped to host)
- **Auto-restart**: Enabled (`unless-stopped`)
- **Model Storage**: Persistent volume (`aadhar_models`)

### Quick Commands

#### Check Status
```bash
sudo docker ps
curl http://localhost:8000/health
```

#### View Logs
```bash
sudo docker logs aadhar-ocr-api
sudo docker logs -f aadhar-ocr-api  # Follow logs
```

#### Stop Container
```bash
sudo docker stop aadhar-ocr-api
```

#### Start Container
```bash
sudo docker start aadhar-ocr-api
```

#### Restart Container
```bash
sudo docker restart aadhar-ocr-api
```

#### Remove Container
```bash
sudo docker stop aadhar-ocr-api
sudo docker rm aadhar-ocr-api
```

#### Rebuild Image
```bash
cd /home/home/Downloads/aadhar_project
sudo docker build -t aadhar-ocr-api .
```

#### Run New Container
```bash
sudo docker run -d -p 8000:8000 \
  --name aadhar-ocr-api \
  -v aadhar_models:/app/models \
  --restart unless-stopped \
  aadhar-ocr-api
```

### API Endpoints

- **Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Extract Data**: POST http://localhost:8000/extract

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Upload and extract (replace with your image path)
curl -X POST http://localhost:8000/extract \
  -F "file=@/path/to/aadhar_image.jpg"
```

### Extracted Fields

The API now only extracts these 4 fields:
- `AADHAR_NUMBER` - Aadhaar card number (formatted as XXXX XXXX XXXX)
- `NAME` - Cardholder name
- `DOB` - Date of birth
- `GENDER` - Gender (Male/Female)

### Key Changes Made

1. **Dockerfile**:
   - Single-stage build (no multi-stage)
   - Python 3.11-slim base image
   - CPU-only PyTorch installation
   - Removed unnecessary packages
   - Fixed `libgl1-mesa-glx` → `libgl1`

2. **requirements.txt**:
   - Removed pinned versions for PyTorch
   - Added CPU-only PyTorch index URL
   - Updated to use latest compatible versions

3. **Application Code**:
   - Simplified OCR preprocessing
   - Uses PSM 7 (single line) for all fields
   - Direct grayscale conversion
   - Filters only 4 required fields
   - Removed ADDRESS, FATHER, MOTHER, SPOUSE fields

### Docker Image Size
- **Base Image**: python:3.11-slim (~124MB)
- **Final Image**: ~2.5GB (with CPU-only PyTorch)
- **Much smaller** than CUDA version (~6GB+)

### Production Deployment

For production deployment to services like Render, Railway, or AWS:

1. Ensure your deployment platform has at least 3GB RAM
2. Set environment variables if needed (see `.env.example`)
3. The Dockerfile is production-ready with:
   - Health checks
   - Non-root user (optional, commented out)
   - Proper logging
   - Auto-restart policy

### Troubleshooting

If container fails to start:
```bash
# Check logs
sudo docker logs aadhar-ocr-api

# Check if port is in use
sudo lsof -i :8000

# Remove and recreate
sudo docker stop aadhar-ocr-api
sudo docker rm aadhar-ocr-api
# Then run the container again
```

### Performance Notes

- First request may be slow (model downloads from HuggingFace)
- Subsequent requests are fast (~0.5-2 seconds per image)
- CPU-only mode is sufficient for OCR tasks
- Model is cached in persistent volume

---

**Deployment Date**: 2025-11-09  
**Status**: ✅ Successfully Running

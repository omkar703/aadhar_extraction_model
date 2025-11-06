# Aadhaar Card Extraction API - Project Overview

## 📁 Complete File Structure

```
aadhar_extraction_model/
├── app/                          # Application source code
│   ├── __init__.py              # Package initializer
│   ├── main.py                  # FastAPI application & endpoints
│   ├── models.py                # Pydantic response models
│   ├── processing.py            # YOLO + OCR processing logic
│   └── utils.py                 # Model loading utilities
│
├── Scripts/                      # Deployment & management scripts
│   ├── start.sh                 # Local development startup
│   ├── start_server.sh          # Production server startup (with daemon mode)
│   ├── stop_server.sh           # Stop background server
│   ├── test_api.sh              # API testing script
│   └── deploy_to_server.sh      # Remote server deployment
│
├── Docker/                       # Container configuration
│   ├── Dockerfile               # Container definition
│   └── .dockerignore            # Docker build exclusions
│
├── Documentation/                # Project documentation
│   ├── README.md                # Main project README
│   ├── QUICK_START.md           # Quick reference guide
│   ├── DEPLOYMENT.md            # Comprehensive deployment guide
│   └── PROJECT_OVERVIEW.md      # This file
│
└── requirements.txt             # Python dependencies
```

---

## 📄 File Descriptions

### Application Code (`app/`)

#### `main.py`
**Purpose:** Core FastAPI application
- Defines API endpoints
- Implements lifespan events for model loading
- Handles file uploads and error responses
- Uses async/await with thread pool for blocking operations

**Key Features:**
- `/` - Health check endpoint
- `/api/v1/extract/` - Main extraction endpoint
- Automatic model loading on startup
- Comprehensive error handling

---

#### `models.py`
**Purpose:** Pydantic models for request/response validation
- Defines `AadhaarResponse` model
- All fields are optional (as detection may not find everything)
- Provides JSON schema for API documentation

**Fields:**
- AADHAR_NUMBER, NAME, ADDRESS, DOB, GENDER, VID
- FATHER_NAME, PHONE_NUMBER (if detected)

---

#### `processing.py`
**Purpose:** Core detection and OCR logic
- Runs YOLO detection on uploaded images
- Extracts text using Tesseract OCR
- Special formatting for Aadhaar numbers (XXXX XXXX XXXX)

**Workflow:**
1. Run YOLO model → detect bounding boxes
2. For each detection:
   - Crop region
   - Convert to grayscale
   - Run Tesseract OCR
   - Clean extracted text
3. Format and return results

---

#### `utils.py`
**Purpose:** Model management utilities
- Singleton pattern for model loading
- Downloads YOLOv8 model from Hugging Face Hub
- Caches model to avoid repeated downloads

---

### Scripts

#### `start.sh`
**Purpose:** Basic local development startup
**Best for:** First-time setup, local testing

```bash
./start.sh
```

**What it does:**
1. Installs Tesseract and system dependencies
2. Creates Python virtual environment
3. Installs Python packages
4. Downloads YOLO model
5. Starts server in foreground with reload

---

#### `start_server.sh`
**Purpose:** Production-ready server startup
**Best for:** Production deployment, remote servers

```bash
# Foreground mode
./start_server.sh

# Background/daemon mode
./start_server.sh daemon
```

**Features:**
- All features from `start.sh`
- Daemon mode for background execution
- Creates PID file (`server.pid`)
- Logs to `server.log`
- Quieter output for production

**Environment Variables:**
- `PORT` - Server port (default: 8000)
- `WORKERS` - Worker processes (default: 2)

---

#### `stop_server.sh`
**Purpose:** Stop background server

```bash
./stop_server.sh
```

Gracefully stops the server started with `start_server.sh daemon`

---

#### `test_api.sh`
**Purpose:** Test API functionality

```bash
# Test local
./test_api.sh

# Test remote
./test_api.sh http://192.168.1.100:8000
```

**Tests:**
- Health check (/)
- Documentation endpoint (/docs)

---

#### `deploy_to_server.sh`
**Purpose:** Interactive remote deployment

```bash
./deploy_to_server.sh
```

**Interactive prompts for:**
- Server IP/hostname
- SSH username
- SSH port
- Deployment path

**Actions:**
1. Tests SSH connection
2. Creates remote directory
3. Copies files via rsync
4. Runs setup on remote server
5. Starts API in background

---

### Docker Files

#### `Dockerfile`
**Purpose:** Container definition for Docker deployment

**Key optimizations:**
- Uses Python 3.10-slim base
- Installs system dependencies (Tesseract, OpenGL)
- Pre-downloads YOLO model during build (baked into image)
- Multi-stage optimization for smaller image size

**Build:**
```bash
docker build -t aadhaar-extractor .
```

**Run:**
```bash
docker run -d -p 8000:8000 --name aadhaar-api aadhaar-extractor
```

---

#### `.dockerignore`
**Purpose:** Excludes unnecessary files from Docker build
- Virtual environments
- Python cache files
- Git files
- Development files

---

### Configuration

#### `requirements.txt`
**Purpose:** Python package dependencies

**Main packages:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `ultralytics` - YOLOv8 framework
- `pytesseract` - OCR wrapper
- `opencv-python-headless` - Image processing
- `huggingface-hub` - Model downloading
- `python-multipart` - File upload support

---

### Documentation

#### `README.md`
Main project documentation with features, setup, and basic usage

#### `QUICK_START.md`
Quick reference for all scripts and common commands

#### `DEPLOYMENT.md`
Comprehensive deployment guide covering:
- Local development
- Remote servers
- Docker deployment
- Production with systemd
- Nginx reverse proxy
- SSL setup
- Monitoring and troubleshooting

---

## 🚀 Quick Command Reference

### Local Development
```bash
./start.sh                    # Start with auto-reload
```

### Production Deployment
```bash
./start_server.sh daemon      # Start in background
./stop_server.sh             # Stop server
tail -f server.log           # View logs
```

### Remote Deployment
```bash
./deploy_to_server.sh        # Interactive deployment
```

### Testing
```bash
./test_api.sh                # Test API
curl http://localhost:8000/  # Health check
```

### Docker
```bash
docker build -t aadhaar-extractor .
docker run -d -p 8000:8000 --name aadhaar-api aadhaar-extractor
docker logs -f aadhaar-api
```

---

## 🔄 Typical Workflows

### Development Workflow
```bash
cd aadhar_extraction_model
./start.sh
# Make changes, server auto-reloads
# Press Ctrl+C to stop
```

### Production Server Setup
```bash
# On local machine
./deploy_to_server.sh
# Follow prompts

# Or manually
scp -r aadhar_extraction_model/ user@server:/path/
ssh user@server
cd /path/aadhar_extraction_model
./start_server.sh daemon
```

### Docker Workflow
```bash
docker build -t aadhaar-extractor .
docker run -d -p 8000:8000 --name aadhaar-api aadhaar-extractor
docker logs -f aadhaar-api
```

---

## 🧪 API Usage

### Health Check
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Aadhaar Card Extraction API is running",
  "status": "healthy",
  "version": "1.0.0"
}
```

### Extract Aadhaar Information
```bash
curl -X POST "http://localhost:8000/api/v1/extract/" \
  -F "image=@/path/to/aadhaar.jpg"
```

**Response:**
```json
{
  "AADHAR_NUMBER": "1234 5678 9012",
  "NAME": "John Doe",
  "ADDRESS": "123 Main Street, City - 123456",
  "DOB": "01/01/1990",
  "GENDER": "Male",
  "VID": null
}
```

### Interactive Documentation
Open in browser:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 🔧 Configuration

### Environment Variables
```bash
# Default
PORT=8000 WORKERS=2 ./start_server.sh daemon

# Custom
PORT=5000 WORKERS=4 ./start_server.sh daemon
```

### Worker Recommendations
- **Development:** 1-2 workers
- **Production (4 cores):** 4-8 workers
- **Production (8 cores):** 8-16 workers

---

## 📊 Monitoring

### Check Status
```bash
ps aux | grep uvicorn           # Process status
curl http://localhost:8000/     # API health
cat server.pid                  # Get PID
```

### View Logs
```bash
tail -f server.log              # Real-time logs
cat server.log                  # All logs
grep ERROR server.log           # Filter errors
```

---

## 🛠️ Troubleshooting

### Common Issues

**Port already in use:**
```bash
sudo lsof -i :8000
kill -9 <PID>
```

**Permission denied:**
```bash
chmod +x *.sh
```

**Tesseract not found:**
```bash
sudo apt-get install tesseract-ocr libtesseract-dev
```

**Model download fails:**
```bash
python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt')"
```

---

## 🎯 Next Steps

1. **Test locally:** `./start.sh`
2. **Deploy to server:** `./deploy_to_server.sh`
3. **Set up monitoring:** See DEPLOYMENT.md
4. **Configure SSL:** Use Let's Encrypt (DEPLOYMENT.md)
5. **Set up reverse proxy:** Nginx configuration (DEPLOYMENT.md)

---

## 📚 Additional Resources

- **QUICK_START.md** - Fast command reference
- **DEPLOYMENT.md** - Detailed deployment guide
- **README.md** - Project introduction

---

## 💡 Tips

1. Always test locally before deploying
2. Use daemon mode for production
3. Monitor logs regularly
4. Keep dependencies updated
5. Use SSL in production
6. Set up firewall rules
7. Regular backups recommended

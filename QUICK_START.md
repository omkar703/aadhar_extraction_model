# Quick Start Guide

## 🚀 Available Scripts

### 1. `start.sh` - Local Development (Original)
Basic startup script with automatic setup.

```bash
./start.sh
```

**Features:**
- Installs system dependencies
- Creates virtual environment
- Installs Python packages
- Downloads YOLO model
- Starts server in foreground with reload

---

### 2. `start_server.sh` - Production Server Script
Enhanced script with daemon mode support.

```bash
# Foreground mode (with reload)
./start_server.sh

# Background/Daemon mode
./start_server.sh daemon

# With custom port and workers
PORT=5000 WORKERS=4 ./start_server.sh daemon
```

**Features:**
- All features from `start.sh`
- Daemon mode for background execution
- PID file tracking
- Log file (server.log)
- Production-ready

---

### 3. `stop_server.sh` - Stop Background Server
Stops the server running in daemon mode.

```bash
./stop_server.sh
```

---

### 4. `test_api.sh` - API Testing
Tests if the API is running correctly.

```bash
# Test local server
./test_api.sh

# Test remote server
./test_api.sh http://192.168.1.100:8000
```

**Tests:**
- Health check endpoint (/)
- Documentation endpoint (/docs)

---

### 5. `deploy_to_server.sh` - Remote Deployment
Interactive script to deploy to a remote server.

```bash
./deploy_to_server.sh
```

**What it does:**
1. Prompts for server details (IP, username, SSH port)
2. Tests SSH connection
3. Copies files via rsync
4. Runs setup on remote server
5. Starts the API in background

**Requirements:**
- SSH access to remote server
- rsync installed locally

---

## 📋 Usage Examples

### Local Development Workflow

```bash
# First time setup and run
cd aadhar_extraction_model
./start.sh

# Server runs, press Ctrl+C to stop
```

### Production Server Workflow

```bash
# Start in daemon mode
./start_server.sh daemon

# Check if running
curl http://localhost:8000/

# View logs
tail -f server.log

# Stop server
./stop_server.sh
```

### Deploy to Remote Server

```bash
# Method 1: Automated
./deploy_to_server.sh
# Follow the prompts

# Method 2: Manual
rsync -avz --exclude 'venv/' ./ user@server:/path/
ssh user@server
cd /path
./start_server.sh daemon
```

### Testing

```bash
# Test local API
./test_api.sh

# Test specific endpoint
curl -X POST "http://localhost:8000/api/v1/extract/" \
  -F "image=@sample.jpg"
```

---

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Build
docker build -t aadhaar-extractor .

# Run
docker run -d -p 8000:8000 --name aadhaar-api aadhaar-extractor

# Logs
docker logs -f aadhaar-api
```

---

## 🔧 Environment Variables

All scripts support these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `WORKERS` | 2 | Number of worker processes |

**Example:**
```bash
PORT=5000 WORKERS=4 ./start_server.sh daemon
```

---

## 📊 Monitoring

### Check if server is running

```bash
# Check process
ps aux | grep uvicorn

# Check with curl
curl http://localhost:8000/

# Check PID file
cat server.pid
```

### View logs

```bash
# Real-time logs
tail -f server.log

# All logs
cat server.log
```

---

## 🛑 Stopping the Server

### If started with `start.sh` (foreground)
Press `Ctrl+C`

### If started with `start_server.sh daemon` (background)
```bash
./stop_server.sh
```

### Manual stop
```bash
# Kill by PID
kill $(cat server.pid)

# Kill by name
pkill -f "uvicorn app.main:app"
```

---

## 💡 Tips

1. **First time?** Use `./start.sh` to test locally
2. **Production?** Use `./start_server.sh daemon`
3. **Remote server?** Use `./deploy_to_server.sh`
4. **Need Docker?** See DEPLOYMENT.md

For detailed deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md)

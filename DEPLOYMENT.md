# Deployment Guide

This guide covers different ways to deploy the Aadhaar Extraction API.

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Remote Server Deployment](#remote-server-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)

---

## 🖥️ Local Development

### Quick Start (Foreground Mode)

```bash
cd aadhar_extraction_model
./start.sh
```

The API will run in foreground mode with auto-reload enabled.

### Daemon Mode (Background)

```bash
./start_server.sh daemon
```

To stop:
```bash
./stop_server.sh
```

View logs:
```bash
tail -f server.log
```

---

## 🌐 Remote Server Deployment

### Method 1: Automated Deployment Script

```bash
./deploy_to_server.sh
```

The script will:
1. Ask for server details (IP, username, port)
2. Test SSH connection
3. Copy application files via rsync
4. Run setup and start the server

### Method 2: Manual Deployment

#### Step 1: Copy files to server

```bash
rsync -avz --exclude 'venv/' --exclude '__pycache__/' \
  ./ user@server:/path/to/deployment/
```

#### Step 2: SSH into server

```bash
ssh user@server
cd /path/to/deployment
```

#### Step 3: Run setup script

**Foreground mode (for testing):**
```bash
./start_server.sh
```

**Daemon mode (for production):**
```bash
./start_server.sh daemon
```

#### Step 4: Configure firewall

```bash
# Allow port 8000
sudo ufw allow 8000
sudo ufw reload
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t aadhaar-extractor:latest .
```

### Run Container

**Basic:**
```bash
docker run -d -p 8000:8000 --name aadhaar-api aadhaar-extractor:latest
```

**With custom configuration:**
```bash
docker run -d \
  --name aadhaar-api \
  -p 8000:8000 \
  -e PORT=8000 \
  -e WORKERS=4 \
  --restart unless-stopped \
  aadhaar-extractor:latest
```

### Container Management

```bash
# View logs
docker logs -f aadhaar-api

# Stop
docker stop aadhaar-api

# Start
docker start aadhaar-api

# Remove
docker rm -f aadhaar-api
```

---

## 🚀 Production Deployment

### Using Systemd (Recommended for Linux Servers)

#### Step 1: Create systemd service file

```bash
sudo nano /etc/systemd/system/aadhaar-api.service
```

Add the following content:

```ini
[Unit]
Description=Aadhaar Extraction API
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/aadhar_extraction_model
Environment="PATH=/path/to/aadhar_extraction_model/venv/bin"
Environment="PORT=8000"
Environment="WORKERS=4"
ExecStart=/path/to/aadhar_extraction_model/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 2: Enable and start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable aadhaar-api
sudo systemctl start aadhaar-api
```

#### Step 3: Check status

```bash
sudo systemctl status aadhaar-api
```

#### View logs

```bash
sudo journalctl -u aadhaar-api -f
```

### Using Nginx as Reverse Proxy

#### Install Nginx

```bash
sudo apt-get install nginx
```

#### Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/aadhaar-api
```

Add:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        
        # Allow large file uploads
        client_max_body_size 10M;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/aadhaar-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

---

## 🧪 Testing Deployment

### Quick Health Check

```bash
./test_api.sh
```

Or manually:

```bash
# Local
curl http://localhost:8000/

# Remote
curl http://your_server_ip:8000/
```

### Test Image Extraction

```bash
curl -X POST "http://your_server:8000/api/v1/extract/" \
  -F "image=@sample_aadhaar.jpg"
```

---

## 🔧 Configuration

### Environment Variables

- `PORT`: Server port (default: 8000)
- `WORKERS`: Number of worker processes (default: 2)

### Recommended Settings

**Development:**
```bash
PORT=8000 WORKERS=1 ./start_server.sh
```

**Production (4 CPU cores):**
```bash
PORT=8000 WORKERS=8 ./start_server.sh daemon
```

**Production (8 CPU cores):**
```bash
PORT=8000 WORKERS=16 ./start_server.sh daemon
```

---

## 📊 Monitoring

### Check Server Status

```bash
# If using systemd
sudo systemctl status aadhaar-api

# If using start_server.sh
ps aux | grep uvicorn
```

### View Logs

```bash
# Using start_server.sh
tail -f server.log

# Using systemd
sudo journalctl -u aadhaar-api -f

# Using docker
docker logs -f aadhaar-api
```

### Monitor Resources

```bash
htop
# or
top
```

---

## 🛠️ Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Permission Denied

```bash
# Make scripts executable
chmod +x *.sh
```

### Tesseract Not Found

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr libtesseract-dev
```

### Model Download Fails

```bash
# Manually download model
python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt')"
```

---

## 🔒 Security Best Practices

1. **Use a reverse proxy** (Nginx/Apache)
2. **Enable SSL/TLS** with Let's Encrypt
3. **Restrict firewall rules** to only necessary ports
4. **Run as non-root user**
5. **Keep dependencies updated**
6. **Set up rate limiting** in Nginx
7. **Monitor logs** for suspicious activity

---

## 📝 Quick Command Reference

```bash
# Local development
./start.sh                    # Foreground with reload
./start_server.sh daemon      # Background mode
./stop_server.sh             # Stop background server
./test_api.sh                # Test API

# Remote deployment
./deploy_to_server.sh        # Automated deployment

# Docker
docker build -t aadhaar-extractor .
docker run -d -p 8000:8000 --name aadhaar-api aadhaar-extractor
docker logs -f aadhaar-api

# Systemd
sudo systemctl start aadhaar-api
sudo systemctl stop aadhaar-api
sudo systemctl status aadhaar-api
sudo journalctl -u aadhaar-api -f
```

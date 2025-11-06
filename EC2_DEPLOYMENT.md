# EC2 Deployment Guide

## EC2 Instance Requirements

### Recommended Instance Type
- **Minimum**: `t3.medium` (2 vCPU, 4 GB RAM)
- **Recommended**: `t3.large` (2 vCPU, 8 GB RAM) or higher
- **Storage**: At least 20 GB EBS volume
- **OS**: Ubuntu 22.04 LTS or Amazon Linux 2023

### Why These Specs?
- **CPU**: YOLOv8-nano model inference requires decent CPU performance
- **RAM**: 4 GB minimum for running the model + FastAPI + workers
- **Storage**: PyTorch, Ultralytics, and dependencies require ~3-4 GB

## Deployment Steps

### 1. Launch EC2 Instance

```bash
# From AWS Console or CLI, launch an Ubuntu 22.04 instance
# Ensure security group allows:
# - Port 22 (SSH) from your IP
# - Port 8000 (API) from 0.0.0.0/0 or specific IPs
```

### 2. Connect to EC2 Instance

```bash
# From your local machine
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 3. Upload Project Files

**Option A: Using SCP**
```bash
# From your local machine (in project directory)
scp -i your-key.pem -r . ubuntu@your-ec2-public-ip:~/aadhar_extraction_model/
```

**Option B: Using Git**
```bash
# On EC2 instance
git clone your-repository-url
cd aadhar_extraction_model
```

**Option C: Using rsync (recommended for updates)**
```bash
# From your local machine
rsync -avz -e "ssh -i your-key.pem" \
  --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  . ubuntu@your-ec2-public-ip:~/aadhar_extraction_model/
```

### 4. Run Setup Script

```bash
# On EC2 instance
cd ~/aadhar_extraction_model
chmod +x start.sh
./start.sh
```

The script will:
1. Install system dependencies (Tesseract OCR, libraries)
2. Verify Python 3 installation
3. Create and activate virtual environment
4. Install Python dependencies
5. Download YOLOv8 model from Hugging Face
6. Start the API server

### 5. Verify Deployment

```bash
# Check if service is running
curl http://localhost:8000/

# Check API docs
curl http://localhost:8000/docs

# From your local machine
curl http://your-ec2-public-ip:8000/
```

## Running as a Background Service

For production, use systemd to run the API as a service:

### Create Systemd Service

```bash
sudo nano /etc/systemd/system/aadhar-api.service
```

Add the following content:

```ini
[Unit]
Description=Aadhaar Card Extraction API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aadhar_extraction_model
Environment="PATH=/home/ubuntu/aadhar_extraction_model/venv/bin:/usr/bin"
Environment="PORT=8000"
Environment="WORKERS=2"
Environment="ENVIRONMENT=production"
ExecStart=/home/ubuntu/aadhar_extraction_model/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable aadhar-api

# Start the service
sudo systemctl start aadhar-api

# Check status
sudo systemctl status aadhar-api

# View logs
sudo journalctl -u aadhar-api -f
```

## Environment Variables

Configure these in your service file or export them before running:

```bash
export PORT=8000              # API port
export WORKERS=2              # Number of uvicorn workers
export ENVIRONMENT=production # production or development
```

## Security Best Practices

### 1. Use Security Groups
```bash
# Allow only necessary ports:
# - Port 22: SSH from your IP only
# - Port 8000: API from specific IPs or behind load balancer
```

### 2. Use HTTPS (Recommended)
Set up an Application Load Balancer with SSL certificate or use nginx reverse proxy:

```bash
sudo apt install nginx certbot python3-certbot-nginx

# Configure nginx reverse proxy
sudo nano /etc/nginx/sites-available/aadhar-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/aadhar-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Enable Firewall
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Regular Updates
```bash
# Update system packages regularly
sudo apt update && sudo apt upgrade -y
```

## Monitoring and Logs

### View Application Logs
```bash
# If running with systemd
sudo journalctl -u aadhar-api -f

# If running manually
# Logs will be in terminal output
```

### Monitor Resource Usage
```bash
# CPU and Memory
htop

# Disk space
df -h

# Check specific process
ps aux | grep uvicorn
```

## Scaling Considerations

### Vertical Scaling
- Upgrade to larger instance type (t3.xlarge, c5.large, etc.)
- Increase worker count: `export WORKERS=4`

### Horizontal Scaling
- Use Application Load Balancer
- Launch multiple EC2 instances
- Use Auto Scaling Group

### Model Optimization
- YOLOv8-nano is already optimized for speed
- Consider using ONNX runtime for faster inference
- Enable GPU instances (g4dn family) for heavy load

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Out of Memory
```bash
# Check memory usage
free -h

# Reduce worker count
export WORKERS=1
```

### Model Download Fails
```bash
# Check internet connectivity
ping google.com

# Manually download model
python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt')"
```

### Dependencies Installation Fails
```bash
# Clear pip cache
rm -rf ~/.cache/pip

# Reinstall dependencies
pip install -r requirements.txt --no-cache-dir --force-reinstall
```

## Cost Optimization

1. **Use t3.medium with reserved instances** for predictable workloads
2. **Use spot instances** for development/testing
3. **Stop instances** when not in use (development)
4. **Use CloudWatch alarms** to monitor and auto-stop idle instances
5. **Enable EBS volume optimization** to reduce I/O costs

## Backup Strategy

```bash
# Create AMI snapshot regularly
aws ec2 create-image --instance-id i-1234567890abcdef0 --name "aadhar-api-backup-$(date +%Y%m%d)"

# Backup application files
tar -czf aadhar-backup-$(date +%Y%m%d).tar.gz ~/aadhar_extraction_model
aws s3 cp aadhar-backup-*.tar.gz s3://your-backup-bucket/
```

## Quick Commands Reference

```bash
# Start service
sudo systemctl start aadhar-api

# Stop service
sudo systemctl stop aadhar-api

# Restart service
sudo systemctl restart aadhar-api

# View logs
sudo journalctl -u aadhar-api -f

# Test API
curl http://localhost:8000/

# Upload test image
curl -X POST "http://localhost:8000/api/v1/extract/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_aadhaar.jpg"
```

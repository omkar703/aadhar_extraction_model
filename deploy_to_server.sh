#!/bin/bash

set -e  # Exit on error

echo "================================================"
echo "Aadhaar Extraction API - Remote Deployment"
echo "================================================"

# Configuration
read -p "Enter remote server IP or hostname: " SERVER_HOST
read -p "Enter SSH username [default: ubuntu]: " SSH_USER
SSH_USER=${SSH_USER:-ubuntu}
read -p "Enter SSH port [default: 22]: " SSH_PORT
SSH_PORT=${SSH_PORT:-22}
read -p "Enter remote deployment path [default: /home/$SSH_USER/aadhaar_api]: " REMOTE_PATH
REMOTE_PATH=${REMOTE_PATH:-/home/$SSH_USER/aadhaar_api}

echo ""
echo "Deployment Configuration:"
echo "  Server: $SSH_USER@$SERVER_HOST:$SSH_PORT"
echo "  Path: $REMOTE_PATH"
echo ""
read -p "Continue with deployment? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "[1/4] Testing SSH connection..."
if ! ssh -p $SSH_PORT -o ConnectTimeout=5 $SSH_USER@$SERVER_HOST "echo 'Connection successful'"; then
    echo "Error: Cannot connect to server. Please check your SSH credentials."
    exit 1
fi

echo ""
echo "[2/4] Creating remote directory..."
ssh -p $SSH_PORT $SSH_USER@$SERVER_HOST "mkdir -p $REMOTE_PATH"

echo ""
echo "[3/4] Copying application files to server..."
rsync -avz -e "ssh -p $SSH_PORT" \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    ./ $SSH_USER@$SERVER_HOST:$REMOTE_PATH/

echo ""
echo "[4/4] Running setup on remote server..."
ssh -p $SSH_PORT $SSH_USER@$SERVER_HOST "cd $REMOTE_PATH && chmod +x start.sh && bash start.sh" &

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "The application is being started on the remote server."
echo "You can monitor it by running:"
echo "  ssh -p $SSH_PORT $SSH_USER@$SERVER_HOST 'cd $REMOTE_PATH && tail -f nohup.out'"
echo ""
echo "To stop the application:"
echo "  ssh -p $SSH_PORT $SSH_USER@$SERVER_HOST 'pkill -f uvicorn'"
echo ""
echo "API will be available at: http://$SERVER_HOST:8000"
echo "API Documentation: http://$SERVER_HOST:8000/docs"
echo ""

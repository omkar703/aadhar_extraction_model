#!/bin/bash

# Quick upload script for EC2 deployment
# This script uses rsync to efficiently upload files to EC2, excluding unnecessary directories

# Configuration - UPDATE THESE VALUES
EC2_KEY_PATH="your-key.pem"           # Path to your EC2 private key
EC2_USER="ubuntu"                      # EC2 user (ubuntu for Ubuntu, ec2-user for Amazon Linux)
EC2_HOST="your-ec2-public-ip"         # EC2 public IP or hostname
EC2_DEST_DIR="~/aadhar_extraction_model"  # Destination directory on EC2

echo "================================================"
echo "EC2 Upload Script"
echo "================================================"
echo ""

# Validate configuration
if [ "$EC2_KEY_PATH" = "your-key.pem" ] || [ "$EC2_HOST" = "your-ec2-public-ip" ]; then
    echo "⚠ ERROR: Please edit this script and update the configuration variables:"
    echo "  - EC2_KEY_PATH: Path to your .pem key file"
    echo "  - EC2_HOST: Your EC2 instance public IP or hostname"
    echo ""
    echo "Example:"
    echo "  EC2_KEY_PATH=\"~/.ssh/my-ec2-key.pem\""
    echo "  EC2_HOST=\"54.123.45.67\""
    exit 1
fi

# Check if key file exists
if [ ! -f "$EC2_KEY_PATH" ]; then
    echo "✗ ERROR: Key file not found: $EC2_KEY_PATH"
    exit 1
fi

# Check if key has correct permissions
KEY_PERMS=$(stat -c %a "$EC2_KEY_PATH" 2>/dev/null || stat -f %A "$EC2_KEY_PATH" 2>/dev/null)
if [ "$KEY_PERMS" != "400" ] && [ "$KEY_PERMS" != "600" ]; then
    echo "⚠ WARNING: Key file should have 400 or 600 permissions"
    echo "Run: chmod 400 $EC2_KEY_PATH"
    read -p "Fix permissions now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        chmod 400 "$EC2_KEY_PATH"
        echo "✓ Permissions fixed"
    fi
fi

echo "Configuration:"
echo "  Key: $EC2_KEY_PATH"
echo "  Host: $EC2_USER@$EC2_HOST"
echo "  Destination: $EC2_DEST_DIR"
echo ""

# Test SSH connection
echo "Testing SSH connection..."
if ssh -i "$EC2_KEY_PATH" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo '✓ SSH connection successful'" 2>/dev/null; then
    echo ""
else
    echo "✗ ERROR: Cannot connect to EC2 instance"
    echo "Please check:"
    echo "  - EC2 instance is running"
    echo "  - Security group allows SSH (port 22) from your IP"
    echo "  - Key file path and EC2 host are correct"
    exit 1
fi

# Upload files using rsync
echo "Uploading files to EC2..."
echo ""

rsync -avz --progress \
    -e "ssh -i $EC2_KEY_PATH -o StrictHostKeyChecking=no" \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    --exclude '.gitignore' \
    --exclude '.DS_Store' \
    --exclude '*.log' \
    --exclude 'test_*.jpg' \
    --exclude 'test_*.png' \
    . "$EC2_USER@$EC2_HOST:$EC2_DEST_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✓ Upload completed successfully!"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. SSH into your EC2 instance:"
    echo "   ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST"
    echo ""
    echo "2. Navigate to the project directory:"
    echo "   cd $EC2_DEST_DIR"
    echo ""
    echo "3. Make scripts executable:"
    echo "   chmod +x *.sh"
    echo ""
    echo "4. Run the setup script:"
    echo "   ./start.sh"
    echo ""
    echo "For detailed instructions, see EC2_DEPLOYMENT.md"
else
    echo ""
    echo "✗ Upload failed"
    exit 1
fi

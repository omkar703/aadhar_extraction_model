# EC2 Deployment Checklist

## Pre-Deployment (Local Machine)

- [ ] Run validation script: `./validate_setup.sh`
- [ ] All Python files have correct syntax
- [ ] All required packages in requirements.txt
- [ ] Documentation files present (README.md, EC2_DEPLOYMENT.md)
- [ ] Scripts are executable (`chmod +x *.sh`)

## EC2 Instance Setup

- [ ] Launch EC2 instance (t3.medium or larger recommended)
- [ ] Configure Security Group:
  - [ ] Allow SSH (port 22) from your IP
  - [ ] Allow HTTP (port 8000) from 0.0.0.0/0 or specific IPs
- [ ] Assign Elastic IP (optional, for static IP)
- [ ] Configure EBS volume (minimum 20 GB)
- [ ] Note down: Public IP, Key file location

## File Upload

- [ ] Update `upload_to_ec2.sh` with:
  - [ ] EC2_KEY_PATH
  - [ ] EC2_HOST (public IP)
- [ ] Set key permissions: `chmod 400 your-key.pem`
- [ ] Run upload script: `./upload_to_ec2.sh`
- [ ] Verify files uploaded successfully

## Initial Deployment (On EC2)

- [ ] SSH into EC2: `ssh -i your-key.pem ubuntu@your-ec2-ip`
- [ ] Navigate to directory: `cd ~/aadhar_extraction_model`
- [ ] Make scripts executable: `chmod +x *.sh`
- [ ] Run setup script: `./start.sh`
- [ ] Wait for all dependencies to install
- [ ] Wait for model to download from Hugging Face
- [ ] Verify server starts without errors

## Verification

- [ ] Test health endpoint: `curl http://localhost:8000/`
- [ ] Test from local machine: `curl http://your-ec2-ip:8000/`
- [ ] Access API docs: `http://your-ec2-ip:8000/docs`
- [ ] Upload test image using API docs interface
- [ ] Verify extraction returns results

## Production Setup (Optional)

- [ ] Create systemd service (see EC2_DEPLOYMENT.md)
- [ ] Enable service: `sudo systemctl enable aadhar-api`
- [ ] Start service: `sudo systemctl start aadhar-api`
- [ ] Verify service status: `sudo systemctl status aadhar-api`
- [ ] Test service restart: `sudo systemctl restart aadhar-api`

## Security Hardening (Recommended)

- [ ] Restrict SSH to specific IP: Update security group
- [ ] Set up nginx reverse proxy (for HTTPS)
- [ ] Configure SSL certificate with Let's Encrypt
- [ ] Enable UFW firewall
- [ ] Set up CloudWatch monitoring
- [ ] Configure automatic backups (AMI snapshots)

## Monitoring Setup

- [ ] Install htop: `sudo apt install htop`
- [ ] Set up log rotation for application logs
- [ ] Configure CloudWatch alarms for:
  - [ ] CPU usage > 80%
  - [ ] Memory usage > 80%
  - [ ] Disk usage > 80%
- [ ] Set up health check monitoring

## Documentation

- [ ] Document EC2 instance details (IP, region, instance type)
- [ ] Document API endpoints for team
- [ ] Create API usage examples
- [ ] Document maintenance procedures

## Testing Checklist

- [ ] Test with valid Aadhaar card image
- [ ] Test with invalid image (should return error)
- [ ] Test with large image file
- [ ] Test concurrent requests
- [ ] Verify extraction accuracy
- [ ] Test all API endpoints

## Post-Deployment

- [ ] Share API URL with team
- [ ] Share API documentation link
- [ ] Set up monitoring alerts
- [ ] Schedule regular backups
- [ ] Create maintenance schedule
- [ ] Document troubleshooting steps

## Quick Commands Reference

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Check service status
sudo systemctl status aadhar-api

# View logs
sudo journalctl -u aadhar-api -f

# Restart service
sudo systemctl restart aadhar-api

# Check disk space
df -h

# Check memory
free -h

# Check CPU
htop

# Test API
curl http://localhost:8000/

# Upload new changes
# (Run from local machine)
./upload_to_ec2.sh
```

## Troubleshooting Quick Checks

If something goes wrong:

1. **Service won't start**
   - [ ] Check logs: `sudo journalctl -u aadhar-api -f`
   - [ ] Check port: `sudo lsof -i :8000`
   - [ ] Check virtual environment: `ls venv/bin/activate`

2. **Out of memory**
   - [ ] Check usage: `free -h`
   - [ ] Reduce workers: Edit service file, set WORKERS=1
   - [ ] Upgrade instance type

3. **Model download fails**
   - [ ] Check internet: `ping google.com`
   - [ ] Check disk space: `df -h`
   - [ ] Manually download model

4. **API returns errors**
   - [ ] Check logs
   - [ ] Verify all dependencies installed: `pip list`
   - [ ] Test Tesseract: `tesseract --version`

## Maintenance Schedule

- **Daily**: Monitor logs and resource usage
- **Weekly**: Review API usage and performance metrics
- **Monthly**: Update system packages, backup data
- **Quarterly**: Review and optimize costs, update dependencies

---

**Important Notes:**
- Keep your EC2 key file secure (never commit to git)
- Always test in development environment first
- Monitor costs regularly
- Keep backups of working configurations
- Document any custom changes made

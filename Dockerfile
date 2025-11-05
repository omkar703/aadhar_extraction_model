# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install system dependencies for Tesseract and OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

# Copy application code
COPY ./app /code/app

# Copy start script
COPY start.sh /code/start.sh

# Download the YOLO model during build (bake into image for faster startup)
RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='arnabdhar/YOLOv8-nano-aadhar-card', filename='model.pt')"

# Make start script executable
RUN chmod +x /code/start.sh

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV WORKERS=2

# Run the application
CMD ["/code/start.sh"]

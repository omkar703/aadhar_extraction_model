#!/bin/bash

# Start the FastAPI application with uvicorn
# PORT and WORKERS can be configured via environment variables
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2}

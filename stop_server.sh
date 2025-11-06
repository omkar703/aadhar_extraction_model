#!/bin/bash

echo "Stopping Aadhaar Extraction API server..."

if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Killing process $PID..."
        kill $PID
        sleep 1
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "Force killing process..."
            kill -9 $PID
        fi
        
        rm server.pid
        echo "✓ Server stopped successfully"
    else
        echo "Process $PID is not running"
        rm server.pid
    fi
else
    # Try to kill by process name
    if pkill -f "uvicorn app.main:app"; then
        echo "✓ Server stopped successfully"
    else
        echo "No running server found"
    fi
fi

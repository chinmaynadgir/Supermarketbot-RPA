#!/bin/bash

# AI-Powered Supermarket Management System Startup Script

echo "Starting Supermarket Management System v2.0"
echo "======================================="

# Ensure script runs from its containing directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/pyvenv.cfg" ] || [ ! -d "venv/lib" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the application
echo "Launching application..."
python main.py

echo "Application closed. Thank you for using the system."

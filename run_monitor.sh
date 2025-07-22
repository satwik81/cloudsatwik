#!/bin/bash

# Threshold Monitor Startup Script
echo "Starting Threshold Monitor System..."

# Check if config file exists
if [ ! -f "config.yaml" ]; then
    echo "Error: config.yaml not found!"
    echo "Please create a configuration file first."
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import yaml, psutil, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Missing dependencies!"
    echo "Please install required packages:"
    echo "  sudo apt install python3-yaml python3-psutil python3-requests"
    exit 1
fi

# Create directories if they don't exist
mkdir -p logs exports

echo "Configuration validated. Starting monitoring system..."
echo "Press Ctrl+C to stop."
echo ""

# Run the monitor
python3 threshold_monitor.py
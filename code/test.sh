#!/bin/bash
# E-sight Test Mode Runner
# Runs the system in simulation mode without hardware

echo "=================================="
echo "  E-sight Test Mode"
echo "=================================="
echo ""
echo "Running in simulation mode (no hardware required)"
echo "Press Ctrl+C to stop"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if using a video file for testing
if [ -z "$1" ]; then
    # Use webcam
    echo "📹 Using webcam for testing"
    python3 detection.py --test --debug
else
    # Use provided video file
    echo "📹 Using video file: $1"
    python3 detection.py --test --debug --video "$1"
fi

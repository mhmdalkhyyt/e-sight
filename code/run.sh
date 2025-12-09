#!/bin/bash
# E-sight Production Mode Runner
# Runs the system with real hardware (requires sudo for GPIO access)

echo "=================================="
echo "  E-sight Production Mode"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script requires sudo for GPIO access"
    echo "Please run: sudo ./run.sh"
    exit 1
fi

echo "✅ Running with sudo privileges"
echo "🚨 Real hardware mode - LED strip will be controlled"
echo "Press Ctrl+C to stop"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the detection system
python3 detection.py "$@"

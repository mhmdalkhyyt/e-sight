#!/bin/bash
# E-sight Installation Script
# For Raspberry Pi 5

set -e  # Exit on error

echo "=================================="
echo "  E-sight Installation Script"
echo "=================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "Installation will continue, but hardware features won't work."
    echo ""
fi

# Check Python version
echo "📌 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi
echo "✅ Python version OK"
echo ""

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
echo "✅ System packages updated"
echo ""

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libopencv-dev \
    libatlas-base-dev \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk3-module \
    git

echo "✅ System dependencies installed"
echo ""

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Install hardware-specific packages
read -p "🔌 Install hardware support (LED strip, GPIO)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing hardware packages..."
    sudo pip install rpi-ws281x
    
    # Check if user wants Pi Camera support
    read -p "📷 Install Raspberry Pi Camera support? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt-get install -y python3-picamera2
    fi
    
    echo "✅ Hardware packages installed"
    echo ""
fi

# Check if YOLO model exists
echo "🔍 Checking for YOLO model..."
if [ ! -f "yolo11n.torchscript" ]; then
    echo "⚠️  YOLO model not found!"
    echo "The model file 'yolo11n.torchscript' is required."
    echo ""
    echo "Options:"
    echo "1. Download a pre-trained YOLO model"
    echo "2. Export your own model using Ultralytics"
    echo ""
    read -p "Download YOLOv8n model now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Downloading YOLOv8n model..."
        python3 << 'EOF'
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.export(format='torchscript')
print("✅ Model exported to yolov8n.torchscript")
print("Rename it to yolo11n.torchscript or update config.yaml")
EOF
    fi
else
    echo "✅ YOLO model found"
fi
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x test.sh run.sh install.sh
echo "✅ Scripts are now executable"
echo ""

# Setup systemd service (optional)
read -p "🚀 Install systemd service for auto-start on boot? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Installing systemd service..."
    sudo cp e-sight.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Service installed"
    echo ""
    echo "To enable auto-start:"
    echo "  sudo systemctl enable e-sight"
    echo "To start now:"
    echo "  sudo systemctl start e-sight"
    echo "To check status:"
    echo "  sudo systemctl status e-sight"
    echo ""
fi

# Final instructions
echo "=================================="
echo "  ✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Test the system (no hardware required):"
echo "   ./test.sh"
echo ""
echo "2. Run with real hardware (requires sudo for GPIO):"
echo "   sudo ./run.sh"
echo ""
echo "3. View/edit configuration:"
echo "   nano config.yaml"
echo ""
echo "4. Check the README for more information"
echo ""
echo "Enjoy your E-sight system! 🚗💡"

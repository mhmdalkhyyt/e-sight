# E-sight Setup Guide

Complete setup instructions for the E-sight human detection system.

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Software Requirements](#software-requirements)
3. [Installation](#installation)
4. [Hardware Setup](#hardware-setup)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)

---

## Hardware Requirements

### Required Hardware
- **Raspberry Pi 5** (or Pi 4/3B+ with reduced performance)
- **Camera**: USB webcam or Raspberry Pi Camera Module
- **LED Strip**: Luxor addressable LED strip (WS281x compatible)
  - 1 meter length
  - 60 LEDs
  - 5V power supply
- **Power Supply**: 
  - 5V 3A for Raspberry Pi
  - Additional 5V power supply for LED strip (recommended for >30 LEDs)
- **Jumper Cables**: For connecting LED strip to GPIO

### Optional Hardware
- PIR motion sensor (HC-SR501) - for triggering detection
- 12V car battery adapter for mobile use

---

## Software Requirements

- **Operating System**: Raspberry Pi OS (64-bit recommended)
- **Python**: 3.8 or higher
- **Disk Space**: Minimum 2GB free space
- **Internet**: Required for initial setup and model download

---

## Installation

### Quick Install (Recommended)

1. **Clone the repository** (or transfer files to your Pi):
   ```bash
   git clone https://github.com/mhmdalkhyyt/e-sight.git
   cd e-sight/code
   ```

2. **Run the installation script**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   
   The script will:
   - Install system dependencies
   - Create a Python virtual environment
   - Install Python packages
   - Optionally install hardware support (GPIO, LED control)
   - Download YOLO model (if needed)
   - Set up systemd service (optional)

3. **Follow the prompts** to customize your installation.

### Manual Installation

If you prefer manual installation or need to troubleshoot:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y python3-pip python3-venv python3-dev \
    libopencv-dev libatlas-base-dev git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install hardware support (on Raspberry Pi only)
sudo pip install rpi-ws281x

# Make scripts executable
chmod +x test.sh run.sh install.sh
```

---

## Hardware Setup

### LED Strip Connection

1. **Identify LED strip pins**:
   - **5V** - Power (red wire)
   - **GND** - Ground (black/white wire)
   - **DIN** - Data input (green/yellow wire)

2. **Connect to Raspberry Pi**:
   - **LED GND** → **Pi GND** (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
   - **LED DIN** → **Pi GPIO 18** (Pin 12)
   - **LED 5V** → **External 5V power supply** (NOT Pi's 5V if using >30 LEDs)

   > ⚠️ **Important**: For LED strips with >30 LEDs, use an external 5V power supply to avoid damaging your Pi. Connect the external power supply ground to Pi's GND.

3. **Wiring Diagram**:
   ```
   Raspberry Pi                LED Strip
   ┌─────────────┐            ┌──────────┐
   │             │            │          │
   │  GPIO 18 ───┼───────────▶│ DIN      │
   │  (Pin 12)   │            │          │
   │             │            │          │
   │  GND     ───┼───────────▶│ GND      │
   │  (Pin 6)    │            │          │
   │             │            │          │
   └─────────────┘            │ 5V   ────┼──── External 5V PSU
                              │          │
                              └──────────┘
   ```

### Camera Setup

**USB Camera**:
- Simply plug into any USB port
- Camera will be detected as `/dev/video0`

**Raspberry Pi Camera Module**:
1. Connect camera ribbon cable to CSI port
2. Enable camera in raspi-config:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Camera → Enable
   ```

---

## Configuration

### Config File (config.yaml)

Edit `config.yaml` to customize behavior:

```yaml
# Operating Mode
mode:
  test: false        # Set to true for simulation mode
  debug: false       # Enable detailed logging

# Camera Settings
camera:
  source: 0          # 0 for USB camera, or path to video file
  width: 320         # Match the model input size
  height: 240
  fps: 10            # The Pi can't process more than this

# Detection Settings
detection:
  model_path: "yolo11n_320_ncnn_model"
  imgsz: 320                   # Must match the exported model
  confidence_threshold: 0.5    # Higher = fewer false positives
  target_classes: [0]          # 0 = person

# LED Settings
led:
  count: 60          # Number of LEDs
  pin: 18            # GPIO pin (BCM numbering)
  brightness: 5      # 0-255 (keep low for safety)
  duration: 0.5      # How long LED stays lit (seconds)

# Colors (RGB)
colors:
  target: [12, 24, 244]      # Blue for detected person
  neighbor: [0, 255, 0]       # Green for neighbors
  neighbor_dimming: 0.5       # Neighbor brightness factor

# Performance
performance:
  frame_skip: 0      # Skip N frames between detections (0 = none)
  save_frames: false # Save annotated frames (for debugging)
  show_fps: true     # Display FPS counter
```

### Key Settings Explained

- **confidence_threshold**: Lower values (0.3-0.5) detect more objects but with more false positives. Higher values (0.6-0.8) are more selective.
- **brightness**: Keep low (5-20) to avoid distraction while driving. Test in dark conditions.
- **frame_skip**: Leaves the CPU idle between detections (e.g. to run cooler). It does not make each detection faster.
- **model_path / imgsz**: The model's input size is fixed when it is exported. Changing the camera resolution does not change how much work the model does; export a smaller model instead (see README, Performance).

---

## Usage

### Test Mode (No Hardware Required)

Test the system on any computer with a webcam:

```bash
# Basic test with webcam
./test.sh

# Test with video file
./test.sh /path/to/video.mp4

# Or directly:
python3 detection.py --test --debug
```

The LED strip will be simulated in the terminal output.

### Production Mode (Raspberry Pi with Hardware)

```bash
# Run with hardware
sudo ./run.sh

# Or directly:
sudo python3 detection.py

# With custom config:
sudo python3 detection.py --config my_config.yaml
```

> 💡 **Note**: `sudo` is required for GPIO access on Raspberry Pi.

### Auto-Start on Boot

Enable the systemd service to start E-sight automatically when Pi boots:

```bash
# Enable auto-start
sudo systemctl enable e-sight

# Start now
sudo systemctl start e-sight

# Check status
sudo systemctl status e-sight

# View logs
sudo journalctl -u e-sight -f

# Stop service
sudo systemctl stop e-sight

# Disable auto-start
sudo systemctl disable e-sight
```

---

## Testing Individual Components

### Test LED Strip Only

```bash
# Light up LED at position 30 for 2 seconds
sudo python3 interface.py 30 2

# Test different positions
sudo python3 interface.py 0 1   # Left edge
sudo python3 interface.py 30 1  # Center
sudo python3 interface.py 59 1  # Right edge
```

### Test LED Simulator

```bash
python3 led_simulator.py
```

### Test Camera

```bash
# List available cameras
v4l2-ctl --list-devices

# Test camera with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('✅ Camera OK' if ret else '❌ Camera failed'); cap.release()"
```

---

## Troubleshooting

### Camera Issues

**Problem**: "Failed to open camera"
- Check camera connection
- Verify camera is not being used by another process
- Try different camera index: Change `source: 0` to `source: 1` in config.yaml
- For Pi Camera: Enable in `sudo raspi-config`

### LED Issues

**Problem**: LEDs don't light up
- Check wiring (GND and DIN connections)
- Verify GPIO 18 is not used by another process
- Try running with `sudo`
- Test with `interface.py`: `sudo python3 interface.py 30 2`

**Problem**: LEDs flicker or show wrong colors
- Check power supply (may need external 5V PSU)
- Verify LED strip is WS281x compatible
- Try lowering brightness in config.yaml

### Performance Issues

**Problem**: Low FPS (<5 FPS)
- Make sure `model_path` points at the NCNN model, not a `.torchscript` or `.pt` file
- Export a smaller model: `yolo export model=yolo11n.pt format=ncnn imgsz=256` and set `imgsz: 256`
- Check for throttling: `vcgencmd get_throttled` should print `throttled=0x0`
- Close other running applications

**Problem**: High CPU temperature
- Add heatsink or fan to Raspberry Pi
- Enable frame skipping to leave the CPU idle between detections
- Enable frame skipping
- Consider using motion sensor to trigger detection only when needed

### Software Issues

**Problem**: "ModuleNotFoundError"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Problem**: "Permission denied" when accessing GPIO
- Run with sudo: `sudo python3 detection.py`
- Add user to gpio group: `sudo usermod -a -G gpio $USER` (logout required)

**Problem**: Model not found
- Check that the `yolo11n_320_ncnn_model` folder exists in the code directory
- Download model: See installation instructions
- Update path in config.yaml

### Getting Help

If issues persist:
1. Check logs: `sudo journalctl -u e-sight -f` (if using systemd)
2. Run in debug mode: `python3 detection.py --test --debug`
3. Report issue on GitHub with error messages

---

## Performance Benchmarks

No measurements on Raspberry Pi hardware yet. Run with `show_fps: true` and note the result here.

On a 4-core x86 test machine, per frame: YOLO11n TorchScript 640x640 took 74 ms, NCNN 320x320 took 21 ms. Expect a Pi 3B+ to be many times slower than that machine.

---

## Next Steps

1. ✅ Complete hardware setup
2. ✅ Test in simulation mode
3. ✅ Test with real hardware
4. ✅ Calibrate camera position for your car
5. ✅ Adjust LED brightness for night conditions
6. ✅ Fine-tune detection threshold
7. ✅ Set up auto-start (optional)
8. ✅ Install in your car!

**Happy detecting! 🚗💡**

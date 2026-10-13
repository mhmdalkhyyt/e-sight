# E-sight 🚗💡

**Real-time human detection system for enhanced car safety**

A lightweight, camera-based object detection system that uses YOLO to detect humans around your car and displays their position on a 60-LED addressable strip. Built for Raspberry Pi with simplicity and scalability in mind.

---

## 🎯 Project Overview

E-sight improves driver awareness by detecting pedestrians around your vehicle and indicating their position using an LED strip mounted as a heads-up display (HUD). The system runs entirely on a Raspberry Pi, making it affordable and easy to install in any vehicle.

### Key Features

- ✅ **Real-time human detection** using YOLO11/YOLOv8
- ✅ **Visual position indicator** via 60-LED addressable strip
- ✅ **Test mode** - runs without hardware for development/testing
- ✅ **Lightweight & fast** - optimized for Raspberry Pi 5
- ✅ **Auto-start on boot** - systemd service included
- ✅ **Configurable** - YAML-based configuration
- ✅ **Safety features** - confidence thresholds, edge detection filtering

### Demo

When a person is detected:
1. Camera captures the scene
2. YOLO model identifies humans
3. LED strip lights up at corresponding horizontal position
4. Neighboring LEDs dimly lit for better visibility
5. Non-blocking operation maintains real-time performance

---

## 🔧 Quick Start

### Prerequisites
- Raspberry Pi 5 (or Pi 4/3B+)
- USB webcam or Pi Camera Module
- Luxor addressable LED strip (60 LEDs, WS281x compatible)
- Raspberry Pi OS (64-bit recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/mhmdalkhyyt/e-sight.git
cd e-sight/code

# Run installation script
chmod +x install.sh
./install.sh
```

### Test Without Hardware

```bash
# Test with webcam in simulation mode
./test.sh

# Test with video file
./test.sh /path/to/video.mp4
```

### Run on Raspberry Pi

```bash
# Run with hardware (requires sudo for GPIO)
sudo ./run.sh
```

📚 **[Full Setup Guide](SETUP.md)** - Complete hardware setup, wiring diagrams, and troubleshooting

---

## 📋 Hardware Requirements

| Component | Specification |
|-----------|--------------|
| **Computer** | Raspberry Pi 5 (recommended) or Pi 4/3B+ |
| **Camera** | USB webcam or Raspberry Pi Camera Module |
| **LED Strip** | 1m, 60 LEDs, WS281x addressable (Luxor) |
| **Power** | 5V 3A for Pi + external 5V PSU for LED strip |
| **Cables** | Jumper wires for GPIO connection |

---

## 🎛️ Configuration

Edit `code/config.yaml` to customize:

```yaml
detection:
  confidence_threshold: 0.5  # Detection sensitivity
  target_classes: [0]        # 0 = person in COCO dataset

camera:
  source: 0       # Camera index or video file path
  width: 320      # Match the model input size
  height: 240

led:
  count: 60       # Number of LEDs
  brightness: 5   # 0-255 (keep low for driving safety)
  duration: 0.5   # LED on-time in seconds

performance:
  frame_skip: 0   # Skip N frames between detections
  show_fps: true  # Display performance metrics
```

---

## 📖 Usage

### Command Line Options

```bash
# Test mode (simulation, no hardware)
python3 detection.py --test

# Production mode with debug output
sudo python3 detection.py --debug

# Use video file instead of camera
python3 detection.py --test --video /path/to/video.mp4

# Custom config file
python3 detection.py --config my_config.yaml
```

### Test Individual Components

```bash
# Test LED strip
sudo python3 interface.py 30 2  # Light LED 30 for 2 seconds

# Test LED simulator
python3 led_simulator.py

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✅' if cap.read()[0] else '❌')"
```

### Auto-Start on Boot

```bash
# Enable service
sudo systemctl enable e-sight
sudo systemctl start e-sight

# View logs
sudo journalctl -u e-sight -f
```

---

## 📁 Project Structure

```
e-sight/
├── code/
│   ├── detection.py        # Main detection system
│   ├── camera.py           # Latest-frame camera capture
│   ├── detector.py         # YOLO inference (ncnn runtime, no PyTorch)
│   ├── led_display.py      # LED strip driver used by detection.py
│   ├── interface.py        # Standalone LED test tool (hardware)
│   ├── led_simulator.py    # LED simulation (testing)
│   ├── config.yaml         # Configuration file
│   ├── requirements.txt    # Python dependencies (no PyTorch)
│   ├── requirements-ultralytics.txt  # Optional: PyTorch/Ultralytics backend
│   ├── install.sh          # Installation script
│   ├── test.sh            # Test mode launcher
│   ├── run.sh             # Production launcher
│   └── e-sight.service    # Systemd service file
├── docs/                  # Documentation
├── README.md             # This file
└── SETUP.md             # Complete setup guide
```

---

## 🚀 Performance

The default model is YOLO11n exported to NCNN at 320x320 (`code/yolo11n_320_ncnn_model`). Compared with the previous 640x640 TorchScript model it needs about 4x less compute per frame; on a 4-core test machine it ran about 3.5x faster (74 ms vs 21 ms per frame). These numbers have not been measured on a Raspberry Pi yet: run with `show_fps: true` to see the real frame rate on your hardware.

The Pi runs the model with the ncnn runtime directly, so PyTorch and Ultralytics are not installed there. In a test run the whole detection process peaked at about 155 MB of memory, compared with about 1.1 GB through PyTorch + Ultralytics on the same machine.

To use a different model or size, export it with Ultralytics on a PC (`pip install -r requirements-ultralytics.txt`) and copy the folder to the Pi:

```bash
yolo export model=yolo11n.pt format=ncnn imgsz=320
```

Then set `detection.model_path` and `detection.imgsz` in `config.yaml` to match.

---

## ✨ What's Fixed/Improved

This implementation fixes several issues from the original version:

### Critical Bug Fixes
- ✅ **Correct class ID**: Changed from `[1]` (bicycle) to `[0]` (person)
- ✅ **Fixed typo**: `rint` → `print`
- ✅ **In-process LED control**: the strip is opened once; repeated LED failures stop the system with an error instead of being ignored

### New Features
- ✅ **Test mode**: Simulate LED strip without hardware
- ✅ **Configuration system**: Easy YAML-based settings
- ✅ **Non-blocking LED control**: Threading prevents detection slowdown
- ✅ **FPS counter**: Monitor real-time performance
- ✅ **Safety filters**: Edge margin and confidence thresholds
- ✅ **Auto-start service**: systemd integration

### Performance Optimizations
- ✅ **Removed frame saving**: No unnecessary disk I/O
- ✅ **Frame skipping option**: Better FPS on slower devices
- ✅ **Lower resolution support**: Configurable for performance
- ✅ **NCNN model at 320x320**: Fastest model format on Raspberry Pi
- ✅ **Latest-frame capture**: Detection always runs on the newest camera frame, never on a stale buffered one
- ✅ **Removed Docker overhead**: Direct execution on Pi

---

## 2. Project Phases

### 2.1 Planning and Requirements Gathering

- **Objective:** Detect humans around your car at night using available resources.
- **Resources:**
  - 1x Raspberry Pi 3B+
  - 1x Camera module
  - 1x Addressable LED strip from Luxor (1m, 60 LEDs)
  - Jumper cables
- **Constraints:**
  - Budget-friendly
  - Time-limited
  - Simple and scalable solution

- Detect humans around your car at night using available resources.
- Raspberry Pi 3B+, camera module, Luxor LED strip (1m, 60 LEDs), jumper cables.
- Budget-friendly, time-limited, simple and scalable solution.
### 2.2 Technical Approach

- **Camera-based Object Detection:** Use the installed camera module to capture images of the surrounding area. Implement a machine learning model to detect human-like objects in the images.
- **Raspberry Pi and LED Strip:** Connect the addressable LED strip from Luxor to the Raspberry Pi. Develop a script to control the LED strip based on the x-axis position of the detected objects.
- Camera-based Object Detection: Use camera module for image capture, implement machine learning model for human-like object detection.
- Raspberry Pi and LED Strip: Connect Luxor LED strip to Raspberry Pi. Develop script to control LED strip based on x-axis position of detected objects.

### 2.3 Implementation Steps

- **Hardware Setup:** Connect the camera module and addressable LED strip from Luxor to the Raspberry Pi.
- **Software Development:** Train a machine learning model to detect human-like objects in images. Write a script on the Raspberry Pi to process camera data and control the LED strip based on the detected objects' positions.
- **Testing and Validation:** Test the setup in various nighttime conditions to ensure reliability. Fine-tune the camera placement and software parameters for optimal performance.
- Hardware Setup: Connect camera module and Luxor LED strip to Raspberry Pi.
- Software Development: Train machine learning model for human-like object detection in images. Write script for Raspberry Pi to process camera data and control LED strip.
- Testing and Validation: Test setup in various nighttime conditions, fine-tune camera placement and software parameters.

### 2.4 Proof of Concept (PoC)

- Conduct initial tests in a controlled environment to validate the detection and indication system.
- Test the system in real-world conditions around your car.
- Initial tests in controlled environment to validate detection and indication system.
- Test system in real-world conditions around your car.

### 2.5 Documentation and Review

- Create detailed documentation of the setup, code, and testing results.
- Review the project against the definition of done. Assess the scalability and potential for future enhancements.
- Create detailed documentation of setup, code, and testing results.
- Review project against definition of done, assess scalability and potential for future enhancements.

## 3. Next Steps

- **Hardware Acquisition:** Ensure you have all the necessary hardware components.
- **Software Development:** Begin training the machine learning model. Begin writing the scripts for the Raspberry Pi.
- **Hardware Integration:** Start integrating the camera module and addressable LED strip from Luxor with the Raspberry Pi.
- Hardware Acquisition: Ensure necessary hardware components.
- Software Development: Begin training machine learning model, begin writing scripts for Raspberry Pi.
- Hardware Integration: Start integrating camera module and Luxor LED strip with Raspberry Pi.

## 4. Risks and Mitigation Strategies

- **Risk:** Inaccurate object detection due to environmental factors or camera quality.
  - **Mitigation:** Use a high-quality camera module and implement post-processing techniques to enhance accuracy. Continuously update and refine the machine learning model based on real-world data.
- **Risk:** False positives or negatives leading to unsafe driving conditions.
  - **Mitigation:** Implement a machine learning algorithm to improve the accuracy of the detection system. Continuously update and refine the algorithm based on real-world data.
- **Risk:** Limited battery life on the Raspberry Pi.
  - **Mitigation:** Utilize a 12V battery to power the Raspberry Pi, ensuring sufficient power for the duration of the project.
- **Risk:** Delays in hardware acquisition or software development.
  - **Mitigation:** Maintain a realistic project schedule and allocate sufficient time for each task. Break down larger tasks into smaller, manageable sub-tasks to minimize delays and ensure timely completion.
- Risk: Inaccurate object detection due to environmental factors or camera quality.
  - Mitigation: Use high-quality camera module, implement post-processing techniques to enhance accuracy. Continuously update and refine machine learning model.
- Risk: False positives or negatives leading to unsafe driving conditions.
  - Mitigation: Implement machine learning algorithm to improve accuracy. Continuously update and refine algorithm based on real-world data.
- Risk: Limited battery life on Raspberry Pi.
  - Mitigation: Utilize 12V battery to power Raspberry Pi.
- Risk: Delays in hardware acquisition or software development.
  - Mitigation: Maintain realistic project schedule, allocate time for each task. Break down larger tasks into smaller, manageable sub-tasks.

## 5. Project Schedule

- This project will be completed before the sixth of January 2025.
- **Week 1-2:** Hardware acquisition and research.
- **Week 3-4:** Camera calibration and integration with the Raspberry Pi.
- **Week 5-6:** Machine learning model training and initial testing.
- **Week 7-8:** Development and integration of the LED strip with the Raspberry Pi.
- **Week 9-10:** Final testing and validation of the system.
- **Week 11:** Documentation and presentation preparation.
- Completion before January 6, 2025.
- Week 1-2: Hardware acquisition and research.
- Week 3-4: Camera calibration and integration with Raspberry Pi.
- Week 5-6: Machine learning model training and initial testing.
- Week 7-8: Development and integration of LED strip with Raspberry Pi.
- Week 9-10: Final testing and validation of the system.
- Week 11: Documentation and presentation preparation.

## 6. Git Remote Command

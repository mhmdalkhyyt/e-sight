# E-sight container for Raspberry Pi 3B+ (needs a 64-bit Raspberry Pi OS)
# Build and run with: docker compose up -d --build
FROM ultralytics/ultralytics:latest-arm64

# Build tools for the rpi_ws281x C extension
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# torch, ultralytics and OpenCV already ship in the base image
RUN pip install --no-cache-dir "PyYAML>=6.0" "rpi-ws281x>=5.0.0"

# detection.py imports led_simulator for Color/dim_color even on real hardware
COPY detection.py interface.py led_simulator.py config.yaml yolo11n.torchscript /app/

ENV PYTHONUNBUFFERED=1

CMD ["python3", "detection.py"]

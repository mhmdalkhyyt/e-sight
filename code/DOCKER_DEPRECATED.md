# Docker Support

Native execution on the Pi (`./install.sh`, then `sudo ./run.sh`) is still the recommended setup.

If you prefer a container, `docker-compose.yml` runs `detection.py` with the camera (`/dev/video0`)
and the LED strip (privileged mode, `/dev/mem`, `/dev/vcio`) passed through. It needs a 64-bit
Raspberry Pi OS because the base image is `ultralytics/ultralytics:latest-arm64`:

```bash
cd code
./start.sh   # docker compose up -d --build, then follows the logs
```

## Why native is preferred

Docker adds unnecessary overhead on Raspberry Pi:
- **Performance**: Direct execution is 20-30% faster
- **GPIO Access**: Docker requires privileged mode and complex device mapping
- **Camera Access**: Simpler camera setup without container isolation
- **Resource Usage**: Less memory overhead
- **Complexity**: Easier installation and debugging

## Migration

If you were using Docker before:

1. **Remove old containers**:
   ```bash
   docker stop yolov8_container
   docker rm yolov8_container
   docker rmi custom_yolov8_image
   ```

2. **Install natively**:
   ```bash
   ./install.sh
   ```

3. **Run directly**:
   ```bash
   sudo ./run.sh
   ```

## For Development/Testing Only

If you still want to use Docker for development on non-Pi systems, create your own Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run in test mode (no hardware)
CMD ["python3", "detection.py", "--test"]
```

Then build and run:
```bash
docker build -t e-sight-dev .
docker run --rm -v $(pwd):/app e-sight-dev
```

**Note**: This is for testing only. Production deployment should be directly on Raspberry Pi.

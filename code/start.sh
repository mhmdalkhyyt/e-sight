#!/bin/bash

# Delete old container (if it exists)
docker rm -f yolov8_container || true

# Delete old image (if it exists)
docker rmi custom_yolov8_image || true

# Build the new Docker image
echo "Building Docker image: custom_yolov8_image"
docker build -t custom_yolov8_image .

# Run the new container
echo "Starting container: yolov8_container"
docker run -d --name yolov8_container -p 8000:8000 custom_yolov8_image


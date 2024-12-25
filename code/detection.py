#!/usr/bin/env python3
"""
Object Detection with Raspberry Pi Camera Module.
Utilizes OpenCV's pre-trained models to detect objects and output bounding boxes.
"""

import cv2
import numpy as np
import time
import argparse
from picamera2 import Picamera2

# Load pre-trained model and configuration files for object detection
MODEL_PATH = "ssd_mobilenet_v3_large_coco.pb"
CONFIG_PATH = "ssd_mobilenet_v3_large_coco.pbtxt"
CLASS_NAMES_PATH = "coco.names"

# Load class names
with open(CLASS_NAMES_PATH, "r") as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]

# Initialize pre-trained model
net = cv2.dnn_DetectionModel(MODEL_PATH, CONFIG_PATH)
net.setInputSize(320, 320)  # Input size for the network
net.setInputScale(1.0 / 127.5)  # Scale pixel values to [0,1]
net.setInputMean((127.5, 127.5, 127.5))  # Mean subtraction
net.setInputSwapRB(True)  # Swap red and blue channels

def detect_objects(frame):
    """
    Detect objects in the given frame.
    Args:
        frame (np.ndarray): Frame captured from the camera.
    Returns:
        list: Detected objects with class IDs, confidences, and bounding boxes.
    """
    # Perform detection
    class_ids, confidences, boxes = net.detect(frame, confThreshold=0.5, nmsThreshold=0.4)

    detections = []
    if len(class_ids) > 0:
        for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
            detections.append((class_id, confidence, box))
    return detections

def draw_detections(frame, detections):
    """
    Draw bounding boxes and labels on the frame.
    Args:
        frame (np.ndarray): Frame to draw on.
        detections (list): List of detected objects.
    """
    for class_id, confidence, box in detections:
        x, y, w, h = box
        label = f"{CLASS_NAMES[class_id]}: {confidence:.2f}"
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def main(output_bounding_boxes=False):
    """
    Main function to capture video from the Raspberry Pi camera and perform object detection.
    Args:
        output_bounding_boxes (bool): Whether to output bounding boxes to the CLI.
    """
    picam2 = Picamera2()
    picam2.start()

    print("Press Ctrl-C to quit.")
    time.sleep(2)  # Allow the camera to warm up

    try:
        while True:
            # Capture a frame
            frame = picam2.capture_array()

            # Detect objects
            detections = detect_objects(frame)

            # Output bounding boxes to the CLI if enabled
            if output_bounding_boxes:
                for class_id, confidence, box in detections:
                    label = CLASS_NAMES[class_id]
                    print(f"Detected: {label}, Confidence: {confidence:.2f}, Box: {box}")

            # Draw detections on the frame
            draw_detections(frame, detections)

            # Show the frame in a window
            cv2.imshow("Object Detection", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        picam2.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Object detection with Raspberry Pi camera.")
    parser.add_argument("--cli", action="store_true", help="Output bounding boxes to the CLI.")
    args = parser.parse_args()

    main(output_bounding_boxes=args.cli)


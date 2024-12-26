import cv2
import time
import csv
import os
from picamera2 import Picamera2
from ultralytics import YOLO

# Initialize the camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()


import subprocess

def control_led_strip(index, duration):
    subprocess.run(["sudo", "python", "interface", str(index), str(duration)])

# Load YOLO model
model = YOLO("yolo11n.pt")

# Ensure the results.csv file exists
csv_file = "results.csv"
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["frame", "x_min", "y_min", "x_max", "y_max", "confidence", "class"])

frame_count = 0

try:
    while True:
        # Capture a frame
        frame = picam2.capture_array()

        # Run YOLO inference
        results = model(frame)

        # Save the frame to a file
        frame_filename = f"frame_{frame_count}.png"
        cv2.imwrite(frame_filename, frame)

        # Append detection results to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            for result in results[0].boxes:
                # Extract bounding box details
                bbox = result.xyxy[0].tolist()  # [x_min, y_min, x_max, y_max]
                confidence = result.conf[0].item()  # Confidence score
                class_id = result.cls[0].item()  # Class ID
                writer.writerow([frame_filename, *bbox, confidence, class_id]) 
                control_led_strip(max(bbox[0]-bbox[2]), 2)
                time.sleep(2)

        frame_count += 1

except KeyboardInterrupt:
    print("Stopping the program.")

finally:
    picam2.stop()
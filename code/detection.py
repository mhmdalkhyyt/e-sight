import os
import cv2
from ultralytics import YOLO
import subprocess
import math

# Load the YOLO model
model = YOLO("yolo11n.torchscript")

# Specify the class IDs you want to detect
allowed_class_ids = [1]  # Replace with the class IDs you want to detect

# Open the USB camera (0 is the default camera)
cap = cv2.VideoCapture(0)

# Get frame dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

# Create a directory to save the results
output_dir = "results"
os.makedirs(output_dir, exist_ok=True)

def control_led_strip(index, duration):
    """
    Control the LED strip by lighting up a specific LED.
    Args:
        index (int): Index of the LED to light up (0-59).
        duration (int): Duration to light the LED in seconds.
    """
    subprocess.run(["sudo", "python", "interface.py", str(index), str(duration)])

# Loop through the video frames
frame_count = 0
while cap.isOpened():
    # Read a frame from the camera
    success, frame = cap.read()
    if success:
        # Run YOLO inference on the frame
        results = model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Extract bounding box coordinates and map to LED index
        for box in results[0].boxes:
            cls = int(box.cls[0])  # Extract class ID
            if cls in allowed_class_ids:  # Check if class ID is allowed
                x1, y1, x2, y2 = box.xyxy[0].tolist()  # Bounding box coordinates
                center_x = (x1 + x2) / 2  # Horizontal center of the bounding box
                led_index = int(center_x / frame_width * 59)  # Map to LED index range
                print(f"Class ID={cls}, Bounding Box Center X={center_x}, LED Index={led_index}")

                # Light up the corresponding LED
                control_led_strip(led_index, 1)

        # Save the annotated frame to the results directory
        frame_filename = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, annotated_frame)

        # Increment the frame count
        frame_count += 1
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object
cap.release()


import cv2
import csv
import os
import sys
import time
from ultralytics import YOLO
from rpi_ws281x import Color, Adafruit_NeoPixel

# Calculate the segment width
width = 640
num_segments = 60
segment_width = width / num_segments
print(f"Width of each segment: {segment_width:.2f} pixels")

# Generate the x-coordinates for each segment
x_coordinates = [int(i * segment_width) for i in range(num_segments + 1)]
print(f"X-coordinates of segments: {x_coordinates}")

# Load YOLO model
model = YOLO("yolo11n.pt")

# Ensure the results.csv file exists
csv_file = "results.csv"
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["frame", "x_min", "y_min", "x_max", "y_max", "confidence", "class"])

# Directory containing the images
image_dir = "imgs"

# Get a list of all image files in the directory
image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

# LED strip configuration:
LED_COUNT = 60  # Number of LED pixels
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 5  # Brightness (0 to 255)
LED_INVERT = False  # True to invert signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # Set to '1' for GPIOs 13, 19, 41, 45 or 53
DEFAULT_WAIT_TIME = 2  # Default wait time in seconds

# Specify the target class IDs
TARGET_CLASS_IDS = [1]  # Add your desired class IDs here

# Create and initialize the NeoPixel object
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def light_led_with_neighbors(strip, led_idx, wait_sec, target_color=(12, 24, 244), neighbor_color=(0, 255, 0)):
    """
    Lights up a specific LED with neighbors dimly lit.
    Args:
    strip (Adafruit_NeoPixel): The LED strip object.
    led_idx (int): Index of the target LED.
    wait_sec (int): Time in seconds to light the LEDs.
    target_color (tuple): RGB color of the target LED.
    neighbor_color (tuple): RGB color of the neighboring LEDs.
    """
    dimmed_neighbor_color = (max(0, min(255, int(c * 0.5))) for c in neighbor_color)

    # Light up the target LED
    strip.setPixelColor(led_idx, Color(*target_color))

    # Light up neighbors if within bounds
    if led_idx > 0:  # Previous neighbor
        strip.setPixelColor(led_idx - 1, Color(*dimmed_neighbor_color))
    if led_idx < strip.numPixels() - 1:  # Next neighbor
        strip.setPixelColor(led_idx + 1, Color(*dimmed_neighbor_color))

    strip.show()
    time.sleep(wait_sec)

    # Turn off LEDs
    strip.setPixelColor(led_idx, Color(0, 0, 0))  # Turn off target LED
    if led_idx > 0:
        strip.setPixelColor(led_idx - 1, Color(0, 0, 0))  # Turn off previous neighbor
    if led_idx < strip.numPixels() - 1:
        strip.setPixelColor(led_idx + 1, Color(0, 0, 0))  # Turn off next neighbor
    strip.show()

for image_file in image_files:
    start = time.time()
    # Load the image
    frame = cv2.imread(os.path.join(image_dir, image_file))
    # Run YOLO inference
    results = model(frame)
    # Append detection results to CSV
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        for result in results[0].boxes:
            # Extract bounding box details
            bbox = result.xyxy[0].tolist()  # [x_min, y_min, x_max, y_max]
            confidence = result.conf[0].item()  # Confidence score
            class_id = result.cls[0].item()  # Class ID

            # Check if the class ID is in the target class IDs
            if class_id in TARGET_CLASS_IDS:
                writer.writerow([image_file, *bbox, confidence, class_id])
                print(f"Wrote {class_id} at {bbox}")

                # Light up the corresponding LED with neighbors for 2 seconds
                led_idx = int(class_id) % LED_COUNT  # Ensure class_id is within LED_COUNT range
                light_led_with_neighbors(strip, led_idx, DEFAULT_WAIT_TIME)

    print(f"Processed {image_file} in {(time.time() - start)/1000.0} ms")

print("Finished processing all images.")

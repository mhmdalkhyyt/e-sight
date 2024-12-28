import cv2

def check_camera_resolution():
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # Adjust the index if necessary for your setup

    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return

    # Query the resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Camera resolution: {width}x{height}")

    # Release the camera
    cap.release()

if __name__ == "__main__":
    check_camera_resolution()


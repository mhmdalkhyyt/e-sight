#!/usr/bin/env python3
"""
E-sight Human Detection System
Detects humans using YOLO and displays their position on LED strip
"""

import os
import sys
import cv2
import yaml
import time
import argparse
from pathlib import Path
from threading import Thread, Lock
from queue import Queue
from ultralytics import YOLO

# LED control - import appropriate module based on mode
led_controller = None
led_queue = Queue()
led_lock = Lock()


class FPSCounter:
    """Calculate and display FPS"""
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0.0
    
    def update(self):
        """Update frame count and calculate FPS"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 1.0:  # Update every second
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        print("Creating default config...")
        return create_default_config()
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)


def create_default_config() -> dict:
    """Create default configuration"""
    return {
        'mode': {'test': False, 'debug': False},
        'camera': {'source': 0, 'width': 640, 'height': 480, 'fps': 30},
        'detection': {
            'model_path': 'yolo11n.torchscript',
            'confidence_threshold': 0.5,
            'target_classes': [0],  # person class
            'max_distance': 10.0
        },
        'led': {
            'count': 60, 'pin': 18, 'brightness': 5,
            'frequency': 800000, 'dma': 10, 'invert': False,
            'channel': 0, 'duration': 0.5
        },
        'colors': {
            'target': [12, 24, 244],
            'neighbor': [0, 255, 0],
            'neighbor_dimming': 0.5
        },
        'performance': {
            'frame_skip': 0, 'save_frames': False,
            'output_dir': 'results', 'show_fps': True
        },
        'safety': {
            'min_detection_area': 1000,
            'edge_margin': 0.1
        }
    }


def init_led_controller(config: dict, test_mode: bool):
    """Initialize LED controller (real or simulated)"""
    global led_controller
    
    if test_mode:
        # Use simulator
        from led_simulator import LEDSimulator
        led_controller = LEDSimulator(
            led_count=config['led']['count'],
            brightness=config['led']['brightness']
        )
        led_controller.begin()
        print("✅ LED Simulator initialized")
    else:
        # Use real hardware
        try:
            from rpi_ws281x import Color, Adafruit_NeoPixel
            led_controller = Adafruit_NeoPixel(
                config['led']['count'],
                config['led']['pin'],
                config['led']['frequency'],
                config['led']['dma'],
                config['led']['invert'],
                config['led']['brightness'],
                config['led']['channel']
            )
            led_controller.begin()
            print("✅ Hardware LED strip initialized")
        except ImportError:
            print("❌ rpi_ws281x not available. Install it or use --test mode")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to initialize LED hardware: {e}")
            print("Try running with sudo or check GPIO permissions")
            sys.exit(1)


def led_worker(config: dict, test_mode: bool):
    """Background worker to handle LED updates without blocking detection"""
    from led_simulator import Color, dim_color
    
    target_color = tuple(config['colors']['target'])
    neighbor_color = tuple(config['colors']['neighbor'])
    dimming = config['colors']['neighbor_dimming']
    duration = config['led']['duration']
    led_count = config['led']['count']
    
    while True:
        led_idx = led_queue.get()
        if led_idx is None:  # Shutdown signal
            break
        
        try:
            with led_lock:
                # Calculate dimmed neighbor color
                dimmed = dim_color(neighbor_color, dimming)
                
                # Light up target LED
                led_controller.setPixelColor(led_idx, Color(*target_color))
                
                # Light up neighbors
                if led_idx > 0:
                    led_controller.setPixelColor(led_idx - 1, Color(*dimmed))
                if led_idx < led_count - 1:
                    led_controller.setPixelColor(led_idx + 1, Color(*dimmed))
                
                led_controller.show()
                time.sleep(duration)
                
                # Turn off LEDs
                led_controller.setPixelColor(led_idx, Color(0, 0, 0))
                if led_idx > 0:
                    led_controller.setPixelColor(led_idx - 1, Color(0, 0, 0))
                if led_idx < led_count - 1:
                    led_controller.setPixelColor(led_idx + 1, Color(0, 0, 0))
                
                led_controller.show()
        except Exception as e:
            if config['mode']['debug']:
                print(f"\n❌ LED error: {e}")


def control_led_strip(led_idx: int, frame_width: int, config: dict):
    """
    Queue LED update (non-blocking)
    
    Args:
        led_idx: LED index to light up
        frame_width: Width of camera frame
        config: Configuration dict
    """
    # Validate LED index
    if not (0 <= led_idx < config['led']['count']):
        if config['mode']['debug']:
            print(f"\n⚠️  LED index {led_idx} out of range")
        return
    
    # Add to queue for background worker
    led_queue.put(led_idx)
    
    if config['mode']['debug']:
        print(f"\n🔵 Queued LED {led_idx}")


def is_valid_detection(box, frame_width: int, frame_height: int, config: dict) -> bool:
    """
    Check if detection meets safety criteria
    
    Args:
        box: YOLO detection box
        frame_width: Frame width
        frame_height: Frame height
        config: Configuration dict
    
    Returns:
        True if detection is valid
    """
    x1, y1, x2, y2 = box.xyxy[0].tolist()
    
    # Check minimum area
    area = (x2 - x1) * (y2 - y1)
    if area < config['safety']['min_detection_area']:
        return False
    
    # Check edge margin
    margin = config['safety']['edge_margin']
    margin_x = frame_width * margin
    margin_y = frame_height * margin
    
    if (x1 < margin_x or x2 > frame_width - margin_x or
        y1 < margin_y or y2 > frame_height - margin_y):
        return False
    
    # Check confidence
    conf = float(box.conf[0])
    if conf < config['detection']['confidence_threshold']:
        return False
    
    return True


def main():
    """Main detection loop"""
    parser = argparse.ArgumentParser(description='E-sight Human Detection System')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no hardware required)')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--video', type=str, help='Path to video file for testing')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args
    if args.test:
        config['mode']['test'] = True
    if args.debug:
        config['mode']['debug'] = True
    if args.video:
        config['camera']['source'] = args.video
    
    test_mode = config['mode']['test']
    debug_mode = config['mode']['debug']
    
    print("=" * 80)
    print("🚗 E-sight Human Detection System")
    print("=" * 80)
    print(f"Mode: {'TEST (Simulation)' if test_mode else 'PRODUCTION (Hardware)'}")
    print(f"Debug: {'ON' if debug_mode else 'OFF'}")
    print(f"Camera source: {config['camera']['source']}")
    print(f"Model: {config['detection']['model_path']}")
    print("=" * 80)
    
    # Initialize LED controller
    init_led_controller(config, test_mode)
    
    # Start LED worker thread
    led_thread = Thread(target=led_worker, args=(config, test_mode), daemon=True)
    led_thread.start()
    
    # Load YOLO model
    print("\n📦 Loading YOLO model...")
    try:
        model = YOLO(config['detection']['model_path'])
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        sys.exit(1)
    
    # Open camera
    print("\n📹 Initializing camera...")
    cap = cv2.VideoCapture(config['camera']['source'])
    
    if not cap.isOpened():
        print(f"❌ Failed to open camera: {config['camera']['source']}")
        sys.exit(1)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
    cap.set(cv2.CAP_PROP_FPS, config['camera']['fps'])
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"✅ Camera ready: {frame_width}x{frame_height}")
    
    # Setup output directory if needed
    if config['performance']['save_frames']:
        output_dir = config['performance']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Saving frames to: {output_dir}")
    
    # FPS counter
    fps_counter = FPSCounter()
    frame_count = 0
    allowed_classes = set(config['detection']['target_classes'])
    frame_skip = config['performance']['frame_skip']
    
    print("\n🎯 Starting detection... (Press Ctrl+C to stop)")
    print("-" * 80)
    
    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                if debug_mode:
                    print("\n⚠️  Failed to read frame")
                break
            
            # Frame skipping for performance
            if frame_skip > 0 and frame_count % (frame_skip + 1) != 0:
                frame_count += 1
                continue
            
            # Run YOLO inference
            results = model(frame, verbose=False)
            
            # Process detections
            detections_found = 0
            for box in results[0].boxes:
                cls = int(box.cls[0])
                
                # Check if class is in allowed list (person = 0)
                if cls in allowed_classes:
                    # Validate detection
                    if not is_valid_detection(box, frame_width, frame_height, config):
                        continue
                    
                    detections_found += 1
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    center_x = (x1 + x2) / 2
                    conf = float(box.conf[0])
                    
                    # Map to LED index (0-59)
                    led_idx = int(center_x / frame_width * (config['led']['count'] - 1))
                    
                    if debug_mode:
                        print(f"\n👤 Person detected at x={center_x:.1f} (conf={conf:.2f}) → LED {led_idx}")
                    
                    # Control LED strip
                    control_led_strip(led_idx, frame_width, config)
            
            # Update FPS
            fps = fps_counter.update()
            if config['performance']['show_fps'] and fps > 0:
                status = f"FPS: {fps:.1f} | Detections: {detections_found}"
                if not debug_mode:
                    print(f"\r{status}", end='', flush=True)
            
            # Save frame if enabled
            if config['performance']['save_frames']:
                annotated_frame = results[0].plot()
                frame_filename = os.path.join(
                    config['performance']['output_dir'],
                    f"frame_{frame_count:04d}.jpg"
                )
                cv2.imwrite(frame_filename, annotated_frame)
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping detection...")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        cap.release()
        led_queue.put(None)  # Signal LED worker to stop
        led_thread.join(timeout=2)
        
        # Turn off all LEDs
        if led_controller:
            with led_lock:
                for i in range(config['led']['count']):
                    if test_mode:
                        from led_simulator import Color
                    else:
                        from rpi_ws281x import Color
                    led_controller.setPixelColor(i, Color(0, 0, 0))
                led_controller.show()
        
        print("✅ Shutdown complete")
        print(f"📊 Total frames processed: {frame_count}")


if __name__ == "__main__":
    main()

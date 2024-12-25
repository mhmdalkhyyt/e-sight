#!/usr/bin/env python3
"""
NeoPixel LED control module
Author: Tony DiCola (original), enhanced for modularity and performance.

This module allows lighting specific LEDs on a strip with neighbors dimly lit,
using command-line arguments for LED selection and wait time configuration.
"""

import sys
import time
import signal
from rpi_ws281x import Color, Adafruit_NeoPixel

# LED strip configuration:
LED_COUNT = 60  # Number of LED pixels
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 5  # Brightness (0 to 255)
LED_INVERT = False  # True to invert signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # Set to '1' for GPIOs 13, 19, 41, 45 or 53

DEFAULT_WAIT_TIME = 2  # Default wait time in seconds


def dim_color(color, factor=0.5):
    """
    Dims a color by the specified factor.
    Args:
        color (tuple): RGB color tuple.
        factor (float): Factor to reduce brightness (0.0 - 1.0).
    Returns:
        tuple: Dimmed RGB color.
    """
    return tuple(max(0, min(255, int(c * factor))) for c in color)


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
    dimmed_neighbor_color = dim_color(neighbor_color, 0.5)

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


def signal_handler(sig, frame):
    """
    Gracefully handle Ctrl-C.
    Turns off all LEDs before exiting.
    """
    print("\nExiting gracefully. Turning off LEDs...")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    sys.exit(0)


if __name__ == "__main__":
    # Attach signal handler for Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    # Create and initialize the NeoPixel object
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python interface.py <LED_INDEX> [WAIT_TIME]")
        sys.exit(1)

    try:
        led_idx = int(sys.argv[1])
        if not (0 <= led_idx < LED_COUNT):
            raise ValueError("LED index out of range.")

        # Get optional wait time, default to DEFAULT_WAIT_TIME
        wait_sec = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_WAIT_TIME
        if wait_sec <= 0:
            raise ValueError("Wait time must be greater than 0.")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Lighting LED {led_idx} with neighbors for {wait_sec} seconds...")
    light_led_with_neighbors(strip, led_idx, wait_sec)


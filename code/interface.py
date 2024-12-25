#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.
# Showcases various animations on a strip of NeoPixels.

import time
from rpi_ws281x import *

# LED strip configuration:
LED_COUNT = 60  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10  # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 5  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Define function to wipe a color across the display.
def color_wipe(strip, color, direction="right", wait_ms=50):
    """Wipe color across display a pixel at a time."""
    if direction == "left":
        for i in range(strip.numPixels() - 1, -1, -1):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
    else:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)

# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Initialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    try:
        while True:
            # Wipe red color across the display from left to right.
            color_wipe(strip, Color(255, 0, 0), direction="right")
            # Wipe green color across the display from right to left.
            color_wipe(strip, Color(0, 255, 0), direction="left")
            # Wipe blue color across the display from left to right.
            color_wipe(strip, Color(0, 0, 255), direction="right")
    except KeyboardInterrupt:
        # Turn off LEDs on exit.
        color_wipe(strip, Color(0, 0, 0), wait_ms=10)
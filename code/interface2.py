import time
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 60     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Define functions which animate LEDs in various ways.
def pulseFromCenter(strip, center_pixel, wait_ms=50, fade_steps=10):
    """Pulse color from the specified center pixel with fading effect."""
    brightness = [0] * LED_COUNT

    for step in range(fade_steps):
        for i in range(LED_COUNT):
            distance = abs(i - center_pixel)
            brightness[i] = max(0, 255 - distance * (255 // (fade_steps * 2)))
            if i == center_pixel:
                strip.setPixelColor(i, Color(
                    int(255 * brightness[i] / 255),
                    0,
                    0
                ))  # Center pixel is red with fading
            else:
                strip.setPixelColor(i, Color(
                    int(255 * brightness[i] / 255),
                    int(255 * brightness[i] / 255),
                    int(255 * brightness[i] / 255)
                ))
        strip.show()
        time.sleep(wait_ms/1000.0)

    for step in range(fade_steps):
        for i in range(LED_COUNT):
            brightness[i] = max(0, brightness[i] - (255 // (fade_steps * 2)))
            if i == center_pixel:
                strip.setPixelColor(i, Color(
                    int(255 * brightness[i] / 255),
                    0,
                    0
                ))  # Center pixel is red with fading
            else:
                strip.setPixelColor(i, Color(
                    int(255 * brightness[i] / 255),
                    int(255 * brightness[i] / 255),
                    int(255 * brightness[i] / 255)
                ))
        strip.show()
        time.sleep(wait_ms/1000.0)

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            try:
                center_pixel = int(input("Enter the center pixel index (0-59): "))
                if 0 <= center_pixel < LED_COUNT:
                    pulseFromCenter(strip, center_pixel)
                else:
                    print(f"Invalid index. Please enter a value between 0 and {LED_COUNT-1}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
            except KeyboardInterrupt:
                print("Input loop canceled.")
                break

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)


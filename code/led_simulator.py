#!/usr/bin/env python3
"""
LED Strip Simulator for E-sight Testing
Simulates LED strip behavior without physical hardware
"""

import sys
import time
from typing import Tuple


class LEDSimulator:
    """Simulates a NeoPixel LED strip for testing without hardware"""
    
    def __init__(self, led_count: int = 60, brightness: int = 5):
        """
        Initialize the LED simulator
        
        Args:
            led_count: Number of LEDs in the strip
            brightness: Brightness level (0-255)
        """
        self.led_count = led_count
        self.brightness = brightness
        self.pixels = [(0, 0, 0)] * led_count
        print(f"[LED SIMULATOR] Initialized {led_count} LED virtual strip")
    
    def begin(self):
        """Initialize the strip (compatibility with rpi_ws281x)"""
        pass
    
    def numPixels(self) -> int:
        """Return the number of pixels"""
        return self.led_count
    
    def setPixelColor(self, index: int, color: int):
        """
        Set a pixel color
        
        Args:
            index: LED index
            color: Color value (packed RGB)
        """
        if 0 <= index < self.led_count:
            # Unpack color from integer format (compatibility with Color())
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            self.pixels[index] = (r, g, b)
    
    def show(self):
        """Display the current LED state"""
        self._print_led_strip()
    
    def _print_led_strip(self):
        """Print visual representation of LED strip"""
        # Find which LEDs are lit
        lit_leds = []
        for i, (r, g, b) in enumerate(self.pixels):
            if r > 0 or g > 0 or b > 0:
                lit_leds.append((i, r, g, b))
        
        if not lit_leds:
            return
        
        # Create visual representation
        bar = ['·'] * self.led_count
        
        for idx, r, g, b in lit_leds:
            # Choose symbol based on color
            if r > g and r > b:
                bar[idx] = '🔴'  # Red
            elif g > r and g > b:
                bar[idx] = '🟢'  # Green
            elif b > r and b > g:
                bar[idx] = '🔵'  # Blue
            else:
                bar[idx] = '⚪'  # White/mixed
        
        # Print the bar with position markers
        print(f"\r[LED] {''.join(bar[:30])} | {''.join(bar[30:])}  ", end='', flush=True)
        
        # Also print which LEDs are active
        positions = [str(idx) for idx, _, _, _ in lit_leds]
        if positions:
            print(f"  Active: {', '.join(positions)}", end='')


def Color(r: int, g: int, b: int) -> int:
    """
    Convert RGB to packed color value (compatibility with rpi_ws281x.Color)
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        Packed color value
    """
    return (r << 16) | (g << 8) | b


def dim_color(color: Tuple[int, int, int], factor: float = 0.5) -> Tuple[int, int, int]:
    """
    Dims a color by the specified factor.
    
    Args:
        color: RGB color tuple
        factor: Factor to reduce brightness (0.0 - 1.0)
    
    Returns:
        Dimmed RGB color
    """
    return tuple(max(0, min(255, int(c * factor))) for c in color)


def light_led_with_neighbors(strip, led_idx: int, wait_sec: float,
                            target_color: Tuple[int, int, int] = (12, 24, 244),
                            neighbor_color: Tuple[int, int, int] = (0, 255, 0)):
    """
    Lights up a specific LED with neighbors dimly lit.
    
    Args:
        strip: LED strip object (real or simulated)
        led_idx: Index of the target LED
        wait_sec: Time in seconds to light the LEDs
        target_color: RGB color of the target LED
        neighbor_color: RGB color of the neighboring LEDs
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
    strip.setPixelColor(led_idx, Color(0, 0, 0))
    if led_idx > 0:
        strip.setPixelColor(led_idx - 1, Color(0, 0, 0))
    if led_idx < strip.numPixels() - 1:
        strip.setPixelColor(led_idx + 1, Color(0, 0, 0))

    strip.show()


if __name__ == "__main__":
    """Test the LED simulator"""
    print("LED Simulator Test")
    print("=" * 80)
    
    # Create simulator
    strip = LEDSimulator(60, 5)
    strip.begin()
    
    # Test lighting different positions
    print("\nTesting LED positions...")
    for position in [5, 15, 30, 45, 55]:
        print(f"\n\nLighting LED {position}:")
        light_led_with_neighbors(strip, position, 1.0)
        time.sleep(0.5)
    
    print("\n\n✅ LED simulator test complete!")

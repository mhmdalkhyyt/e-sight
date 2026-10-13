#!/usr/bin/env python3
"""
LED display driver for E-sight
Owns the LED strip for the life of the process and renders the latest
detections from a single background thread.
"""

import sys
import time
from threading import Thread, Lock, Event

from led_simulator import Color, dim_color


class LEDError(RuntimeError):
    """Raised when the LED strip keeps failing to update"""


class LEDDisplay:
    """
    Renders detected positions on the LED strip without blocking detection.

    The detection loop calls update() with the LED indices seen in a frame.
    Each index stays lit for `duration` seconds after it was last seen, so
    the strip always shows the current scene instead of replaying a backlog.
    """

    def __init__(self, strip, config: dict, max_failures: int = 3, refresh_interval: float = 0.02):
        self.strip = strip
        self.led_count = config['led']['count']
        self.duration = config['led']['duration']
        self.target_color = Color(*config['colors']['target'])
        self.neighbor_color = Color(*dim_color(tuple(config['colors']['neighbor']),
                                               config['colors']['neighbor_dimming']))
        self.max_failures = max_failures
        self.refresh_interval = refresh_interval

        self._expiry = {}  # LED index -> time it should turn off
        self._lock = Lock()
        self._stop = Event()
        self._thread = Thread(target=self._run, daemon=True)
        self._error = None

    def start(self):
        """Start the render thread"""
        self._thread.start()

    def update(self, led_indices):
        """
        Mark LEDs as seen in the current frame (non-blocking)

        Args:
            led_indices: LED indices to light up

        Raises:
            LEDError: if the strip has stopped working
        """
        if self._error:
            raise self._error

        until = time.monotonic() + self.duration
        with self._lock:
            for idx in led_indices:
                if 0 <= idx < self.led_count:
                    self._expiry[idx] = until

    def stop(self):
        """Stop the render thread and turn off every LED"""
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=2)
        try:
            self._render({})
        except Exception as e:
            print(f"\n❌ Failed to turn off LEDs: {e}", file=sys.stderr)

    def _frame(self, lit: set) -> dict:
        """Build the pixel map for a set of lit target LEDs"""
        pixels = {}
        for idx in lit:
            for n in (idx - 1, idx + 1):
                if 0 <= n < self.led_count and n not in lit:
                    pixels[n] = self.neighbor_color
        for idx in lit:
            pixels[idx] = self.target_color
        return pixels

    def _render(self, pixels: dict):
        """Write a full frame to the strip"""
        off = Color(0, 0, 0)
        for i in range(self.led_count):
            self.strip.setPixelColor(i, pixels.get(i, off))
        self.strip.show()

    def _run(self):
        shown = None
        failures = 0

        while not self._stop.is_set():
            now = time.monotonic()
            with self._lock:
                self._expiry = {i: t for i, t in self._expiry.items() if t > now}
                lit = set(self._expiry)

            if lit != shown:
                try:
                    self._render(self._frame(lit))
                    shown = lit
                    failures = 0
                except Exception as e:
                    failures += 1
                    print(f"\n❌ LED update failed ({failures}/{self.max_failures}): {e}",
                          file=sys.stderr)
                    if failures >= self.max_failures:
                        self._error = LEDError(f"LED strip failed {failures} times in a row: {e}")
                        return

            self._stop.wait(self.refresh_interval)

#!/usr/bin/env python3
"""
Camera capture for E-sight
Always hands the detection loop the newest camera frame, so a slow model
never works on frames that have been sitting in the driver's buffer.
"""

import cv2
from threading import Thread, Lock, Event


class LatestFrameCamera:
    """
    Wraps cv2.VideoCapture for a live camera.

    A background thread keeps reading frames and keeps only the latest one.
    read() returns the newest frame not yet returned, waiting for one if
    needed. Video files are read in order instead, since dropping frames
    would make test runs depend on how fast the machine is.
    """

    def __init__(self, source, width: int, height: int, fps: int):
        self.cap = cv2.VideoCapture(source)
        self.live = isinstance(source, int)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        # Not every driver honours this; the reader thread covers the rest
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._frame = None
        self._ok = True
        self._lock = Lock()
        self._new_frame = Event()
        self._stop = Event()
        self._thread = None

    def isOpened(self) -> bool:
        return self.cap.isOpened()

    def get(self, prop):
        return self.cap.get(prop)

    def start(self):
        """Start the background reader (live cameras only)"""
        if self.live:
            self._thread = Thread(target=self._run, daemon=True)
            self._thread.start()
        return self

    def _run(self):
        while not self._stop.is_set():
            ok, frame = self.cap.read()
            with self._lock:
                self._ok = ok
                if ok:
                    self._frame = frame
            self._new_frame.set()
            if not ok:
                break

    def read(self, timeout: float = 5.0):
        """
        Return (success, frame) with the newest frame.

        Args:
            timeout: Seconds to wait for a new frame from a live camera
        """
        if not self.live:
            return self.cap.read()

        if not self._new_frame.wait(timeout):
            return False, None
        with self._lock:
            self._new_frame.clear()
            return self._ok, self._frame

    def release(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        self.cap.release()

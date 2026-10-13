#!/usr/bin/env python3
"""
YOLO person detector for E-sight
Runs an NCNN-exported YOLO model directly with the ncnn runtime, so the Pi
doesn't need PyTorch or Ultralytics installed. The Ultralytics backend is
kept for running other model formats on a PC.
"""

from pathlib import Path

import cv2
import numpy as np


def create_detector(config: dict):
    """Create the detector selected by detection.backend in the config"""
    det = config['detection']
    backend = det.get('backend', 'ncnn')
    kwargs = dict(
        model_path=det['model_path'],
        imgsz=det.get('imgsz', 320),
        conf=det['confidence_threshold'],
        classes=det['target_classes'],
        threads=det.get('threads', 3),
    )
    if backend == 'ncnn':
        return NCNNDetector(**kwargs)
    if backend == 'ultralytics':
        return UltralyticsDetector(**kwargs)
    raise ValueError(f"Unknown detection backend: {backend} (use 'ncnn' or 'ultralytics')")


class NCNNDetector:
    """
    YOLO detector using the ncnn runtime directly.

    detect() returns a list of (x1, y1, x2, y2, conf) in frame pixels for the
    configured classes, after confidence filtering and NMS.
    """

    def __init__(self, model_path: str, imgsz: int, conf: float, classes, threads: int = 3,
                 iou: float = 0.7):
        import ncnn

        model_dir = Path(model_path)
        param = model_dir if model_dir.is_file() else next(model_dir.glob('*.param'))

        self.net = ncnn.Net()
        self.net.opt.num_threads = threads
        self.net.opt.use_vulkan_compute = False
        if self.net.load_param(str(param)) != 0 or self.net.load_model(str(param.with_suffix('.bin'))) != 0:
            raise RuntimeError(f"Could not load NCNN model from {model_path}")

        self.ncnn = ncnn
        self.input_name = self.net.input_names()[0]
        self.output_name = sorted(self.net.output_names())[0]
        self.imgsz = imgsz
        self.conf = conf
        self.iou = iou
        self.class_rows = [4 + int(c) for c in classes]

    def _letterbox(self, frame):
        """Resize keeping aspect ratio and pad to imgsz x imgsz"""
        h, w = frame.shape[:2]
        r = min(self.imgsz / h, self.imgsz / w)
        new_w, new_h = int(round(w * r)), int(round(h * r))
        pad_x = (self.imgsz - new_w) / 2
        pad_y = (self.imgsz - new_h) / 2
        if (new_w, new_h) != (w, h):
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(pad_y - 0.1)), int(round(pad_y + 0.1))
        left, right = int(round(pad_x - 0.1)), int(round(pad_x + 0.1))
        frame = cv2.copyMakeBorder(frame, top, bottom, left, right,
                                   cv2.BORDER_CONSTANT, value=(114, 114, 114))
        return frame, r, left, top

    def detect(self, frame):
        img, r, pad_x, pad_y = self._letterbox(frame)

        mat = self.ncnn.Mat.from_pixels(img, self.ncnn.Mat.PixelType.PIXEL_BGR2RGB,
                                        self.imgsz, self.imgsz)
        mat.substract_mean_normalize([], [1 / 255.0] * 3)
        with self.net.create_extractor() as ex:
            ex.input(self.input_name, mat)
            _, out = ex.extract(self.output_name)
        out = np.array(out)  # (4 + num_classes, num_anchors): cx, cy, w, h, class scores

        scores = out[self.class_rows].max(axis=0)
        keep = scores >= self.conf
        if not keep.any():
            return []
        cx, cy, bw, bh = out[:4, keep]
        scores = scores[keep]

        # NMS on (x, y, w, h) boxes in model input space
        nms_boxes = np.stack([cx - bw / 2, cy - bh / 2, bw, bh], axis=1)
        idx = cv2.dnn.NMSBoxes(nms_boxes.tolist(), scores.tolist(), self.conf, self.iou)
        idx = np.array(idx, dtype=int).reshape(-1)

        # Undo letterbox to get frame pixel coordinates
        h, w = frame.shape[:2]
        x1 = np.clip((cx[idx] - bw[idx] / 2 - pad_x) / r, 0, w)
        y1 = np.clip((cy[idx] - bh[idx] / 2 - pad_y) / r, 0, h)
        x2 = np.clip((cx[idx] + bw[idx] / 2 - pad_x) / r, 0, w)
        y2 = np.clip((cy[idx] + bh[idx] / 2 - pad_y) / r, 0, h)
        return list(zip(x1.tolist(), y1.tolist(), x2.tolist(), y2.tolist(), scores[idx].tolist()))


class UltralyticsDetector:
    """
    YOLO detector using Ultralytics (needs PyTorch).

    Accepts any model format Ultralytics can load. Same detect() output as
    NCNNDetector.
    """

    def __init__(self, model_path: str, imgsz: int, conf: float, classes, threads: int = 3):
        import torch
        from ultralytics import YOLO

        torch.set_num_threads(threads)
        self.model = YOLO(model_path, task='detect')
        self.imgsz = imgsz
        self.conf = conf
        self.classes = list(classes)

    def detect(self, frame):
        boxes = self.model(frame, imgsz=self.imgsz, conf=self.conf,
                           classes=self.classes, verbose=False)[0].boxes
        return [(*xyxy, c) for xyxy, c in zip(boxes.xyxy.tolist(), boxes.conf.tolist())]


def draw_detections(frame, detections):
    """Return a copy of frame with detection boxes drawn on it"""
    out = frame.copy()
    for x1, y1, x2, y2, conf in detections:
        cv2.rectangle(out, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(out, f"person {conf:.2f}", (int(x1), max(int(y1) - 5, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return out

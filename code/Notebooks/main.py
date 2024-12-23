from pathlib import Path
import gc
import openvino as ov
from ultralytics import YOLO

import notebook_utils as utils

# A directory where the model will be downloaded.

# The name of the model
model_name = "yolov8n"

det_model_path = Path(f"{model_name}_openvino_model/{model_name}.xml")

# export model to OpenVINO format using Ultralytics API
if not det_model_path.exists():
    pt_model = YOLO(f"{model_name}.pt")
    pt_model.export(format="openvino", dynamic=True, half=True)
    del pt_model
    gc.collect()
# Initialize

core = ov.Core()

device = utils.device_widget()
print(device)

core = ov.Core()


def load_model(det_model_path, device):
    compiled_model = compile_model(det_model_path, device)
    det_model = YOLO(det_model_path.parent, task="detect")

    if det_model.predictor is None:
        custom = {"conf": 0.25, "batch": 1, "save": False, "mode": "predict"}  # method defaults
        args = {**det_model.overrides, **custom}
        det_model.predictor = det_model._smart_load("predictor")(overrides=args, _callbacks=det_model.callbacks)
        det_model.predictor.setup_model(model=det_model.model)

    det_model.predictor.model.ov_compiled_model = compiled_model
    return det_model


def compile_model(det_model_path, device):
    det_ov_model = core.read_model(det_model_path)

    ov_config = {}
    if device != "CPU":
        det_ov_model.reshape({0: [1, 3, 640, 640]})
    if "GPU" in device or ("AUTO" in device and "GPU" in core.available_devices):
        ov_config = {"GPU_DISABLE_WINOGRAD_CONVOLUTION": "YES"}
    det_compiled_model = core.compile_model(det_ov_model, device, ov_config)
    return det_compiled_model


det_model = load_model(det_model_path, device.value)

from IPython import display
import cv2
import numpy as np


# Main processing function to run object detection.
def run_object_detection(
    source=0,
    flip=False,
    use_popup=False,
    skip_first_frames=0,
):
    player = None
    try:
        # Create a video player to play with target fps.
        player = utils.VideoPlayer(source=source, flip=flip, fps=30, skip_first_frames=skip_first_frames)
        # Start capturing.
        player.start()
        if use_popup:
            title = "Press ESC to Exit"
            cv2.namedWindow(winname=title, flags=cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE)

        while True:
            # Grab the frame.
            frame = player.next()
            if frame is None:
                print("Source ended")
                break
            # If the frame is larger than full HD, reduce size to improve the performance.
            scale = 1280 / max(frame.shape)
            if scale < 1:
                frame = cv2.resize(
                    src=frame,
                    dsize=None,
                    fx=scale,
                    fy=scale,
                    interpolation=cv2.INTER_AREA,
                )
            # Get the results.
            input_image = np.array(frame)
            detections = det_model(input_image, verbose=False)
            frame = detections[0].plot()

            # Use this workaround if there is flickering.
            if use_popup:
                cv2.imshow(winname=title, mat=frame)
                key = cv2.waitKey(1)
                # escape = 27
                if key == 27:
                    break
            else:
                # Encode numpy array to jpg.
                _, encoded_img = cv2.imencode(ext=".jpg", img=frame, params=[cv2.IMWRITE_JPEG_QUALITY, 100])
                # Create an IPython image.
                i = display.Image(data=encoded_img)
                # Display the image in this notebook.
                display.clear_output(wait=True)
                display.display(i)
    # ctrl-c
    except KeyboardInterrupt:
        print("Interrupted")
    # any different error
    except RuntimeError as e:
        print(e)
    finally:
        if player is not None:
            # Stop capturing.
            player.stop()
        if use_popup:
            cv2.destroyAllWindows()
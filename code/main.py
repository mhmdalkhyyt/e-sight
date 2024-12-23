from ultralytics import YOLO

# Load a YOLO11n PyTorch model
model = YOLO("yolo11n.pt")

# Export the model to NCNN format
model.export(format="ncnn")  # creates 'yolo11n_ncnn_model'

# Load the exported NCNN model
ncnn_model = YOLO("yolo11n_ncnn_model")

# Run inference
results = ncnn_model("https://ultralytics.com/images/bus.jpg")


print("cam done")

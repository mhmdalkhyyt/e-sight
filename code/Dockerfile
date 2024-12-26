# Use the base image
FROM ultralytics/ultralytics:latest-arm64

# Install dependencies to create a virtual environment
RUN apt-get update && apt-get install -y python3.11-venv

# Set the working directory
WORKDIR /app

# Copy your Python scripts into the container
COPY detection.py interface.py /app/

# Copy the requirements file into the container
COPY requirements.txt /app/

#RUN apt install libgl1 -y


# Create a virtual environment and activate it
RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir setuptools==65.5.1 PiDNG

# Expose port if needed
EXPOSE 8000

# Set the command to run your main script
#CMD ["python", "detection.py"]


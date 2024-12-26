# Base image
FROM ultralytics/ultralytics:latest-arm64

# Set the working directory
WORKDIR /app

# Copy your Python scripts into the container
COPY detection.py interface.py /app/

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Expose port if needed
EXPOSE 8000

# Set the command to run your main script
CMD ["python", "interface.py"]


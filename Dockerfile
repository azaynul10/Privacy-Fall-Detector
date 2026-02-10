# Use Python 3.10 slim image for smaller size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# ffmpeg for audio processing
# libsm6, libxext6, libgl1-mesa-glx for OpenCV
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Run the application
CMD ["python", "app.py"]

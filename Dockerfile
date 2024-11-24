# Use a base Python image compatible with Raspberry Pi
FROM python:3.9-buster

# Add metadata to the image
LABEL authors="sayakghorai"

# Install necessary system libraries for GUI and OpenCV
RUN apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    tk \
    libxcb-shm0 \
    libxcb-xfixes0 \
    libxkbcommon-x11-0 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Clone the GitHub repository
RUN git clone https://github.com/sayakghorai34/Human-Detection-and-Counting.git /app

# Create and activate a virtual environment
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Allow GUI applications to connect to the host's display
ENV DISPLAY=:0
ENV LIBGL_ALWAYS_INDIRECT=1

# Expose the necessary port for camera access
CMD ["bash", "-c", "source .venv/bin/activate && python app.py"]

# Hugging Face Spaces Dockerfile for TrackFlow AI (FastAPI)
FROM python:3.11-slim

# System deps (ffmpeg for video handling, libgl for OpenCV)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Env defaults for Spaces
ENV API_HOST=0.0.0.0
ENV API_PORT=7860
ENV ALLOWED_ORIGINS=*

# Expose HF port
EXPOSE 7860

# Start FastAPI via uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]

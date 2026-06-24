FROM python:3.12-slim

# FFmpeg + ffprobe and mount tooling are present in the backend image so that
# preflight/ffprobe and (optional) in-container mounts work. The Process Manager
# image is the one that actually spawns long-running FFmpeg stream processes.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        cifs-utils \
        nfs-common \
        rclone \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

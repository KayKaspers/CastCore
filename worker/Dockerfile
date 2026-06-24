FROM python:3.12-slim

# FFmpeg/ffprobe for media analysis & thumbnail generation jobs.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["arq", "app.worker.WorkerSettings"]

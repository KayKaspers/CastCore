FROM python:3.12-slim

# FFmpeg/ffprobe are required: this service spawns the actual stream processes.
# See backend/Dockerfile for the FFMPEG_VARIANT=static option (CVE-2026-8461 / 8.1.2+).
ARG FFMPEG_VARIANT=apt
ARG FFMPEG_STATIC_URL=""
RUN set -eux; \
    apt-get update; \
    if [ "$FFMPEG_VARIANT" = "static" ] && [ -n "$FFMPEG_STATIC_URL" ]; then \
        apt-get install -y --no-install-recommends curl xz-utils ca-certificates; \
        curl -fsSL "$FFMPEG_STATIC_URL" -o /tmp/ff.tar.xz; \
        mkdir -p /tmp/ff && tar -xf /tmp/ff.tar.xz -C /tmp/ff --strip-components=1; \
        (install -m755 /tmp/ff/bin/ffmpeg /tmp/ff/bin/ffprobe /usr/bin/ \
         || install -m755 /tmp/ff/ffmpeg /tmp/ff/ffprobe /usr/bin/); \
        rm -rf /tmp/ff /tmp/ff.tar.xz; \
    else \
        apt-get install -y --no-install-recommends ffmpeg; \
    fi; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "-m", "app.main"]

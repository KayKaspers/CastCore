FROM python:3.12-slim-trixie

# FFmpeg + ffprobe and mount tooling are present in the backend image so that
# preflight/ffprobe and (optional) in-container mounts work. The Process Manager
# image is the one that actually spawns long-running FFmpeg stream processes.
#
# Security note (CVE-2026-8461 / "PixelSmash", MagicYUV decoder, fixed in FFmpeg 8.1.2):
# Debian's packaged FFmpeg may lag behind security fixes. To ship a patched build, build with
#   --build-arg FFMPEG_VARIANT=static --build-arg FFMPEG_STATIC_URL=<url to an 8.1.2+ tarball>
# The tarball must contain `ffmpeg`/`ffprobe` (optionally under bin/); they install to
# /usr/bin so FFMPEG_PATH stays /usr/bin/ffmpeg. CastCore also detects the running version at
# runtime and warns if it is below 8.1.2.
ARG FFMPEG_VARIANT=apt
ARG FFMPEG_STATIC_URL=""
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends cifs-utils nfs-common rclone curl; \
    if [ "$FFMPEG_VARIANT" = "static" ] && [ -n "$FFMPEG_STATIC_URL" ]; then \
        apt-get install -y --no-install-recommends xz-utils ca-certificates; \
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
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]

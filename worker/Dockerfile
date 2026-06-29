# syntax=docker/dockerfile:1

# ── FFmpeg / ffprobe provisioning (see backend/Dockerfile for the full rationale) ────────────
# FFmpeg/ffprobe for media analysis & thumbnail jobs. This service processes media from
# (potentially untrusted) storage sources and also runs as a non-root user. Variant via
# FFMPEG_VARIANT: copy (default, pinned static image) | static (tarball+SHA256) | apt (fallback).
# For copy/static the build FAILS if ffmpeg/ffprobe < FFMPEG_MIN_VERSION (CVE-2026-8461).
ARG FFMPEG_IMAGE=mwader/static-ffmpeg:8.1.2@sha256:33f770f812cbfc3de96c547157fc9faf8bd95a36481753439ffa761045167585
ARG FFMPEG_VARIANT=copy
ARG FFMPEG_MIN_VERSION=8.1.2

FROM ${FFMPEG_IMAGE} AS ff_copy_bin
FROM python:3.12-slim-trixie AS ff_copy
COPY --from=ff_copy_bin /ffmpeg /ffprobe /out/

FROM python:3.12-slim-trixie AS ff_static
ARG FFMPEG_STATIC_URL=""
ARG FFMPEG_STATIC_SHA256=""
RUN set -eux; \
    [ -n "$FFMPEG_STATIC_URL" ] && [ -n "$FFMPEG_STATIC_SHA256" ] \
        || { echo "FFMPEG_VARIANT=static requires FFMPEG_STATIC_URL and FFMPEG_STATIC_SHA256"; exit 1; }; \
    apt-get update; apt-get install -y --no-install-recommends curl xz-utils ca-certificates; \
    curl -fsSL "$FFMPEG_STATIC_URL" -o /tmp/ff.tar.xz; \
    echo "${FFMPEG_STATIC_SHA256}  /tmp/ff.tar.xz" | sha256sum -c -; \
    mkdir -p /tmp/ff /out; tar -xf /tmp/ff.tar.xz -C /tmp/ff --strip-components=1; \
    (cp /tmp/ff/bin/ffmpeg /tmp/ff/bin/ffprobe /out/ || cp /tmp/ff/ffmpeg /tmp/ff/ffprobe /out/); \
    rm -rf /tmp/ff /tmp/ff.tar.xz /var/lib/apt/lists/*

FROM python:3.12-slim-trixie AS ff_apt
RUN install -d /out

FROM ff_${FFMPEG_VARIANT} AS ffsrc

# ── Final image ──────────────────────────────────────────────────────────────
FROM python:3.12-slim-trixie
ARG FFMPEG_VARIANT=copy
ARG FFMPEG_MIN_VERSION=8.1.2

COPY --from=ffsrc /out/ /tmp/ffsrc/
RUN set -eux; \
    if [ "$FFMPEG_VARIANT" = "apt" ]; then \
        apt-get update; apt-get install -y --no-install-recommends ffmpeg; rm -rf /var/lib/apt/lists/*; \
    else \
        install -m755 /tmp/ffsrc/ffmpeg /tmp/ffsrc/ffprobe /usr/bin/; \
    fi; \
    rm -rf /tmp/ffsrc; \
    ffmpeg -version; ffprobe -version; \
    if [ "$FFMPEG_VARIANT" != "apt" ]; then \
        fv="$(ffmpeg  -version | sed -nE 's/^ffmpeg version n?([0-9]+\.[0-9]+(\.[0-9]+)?).*/\1/p'  | head -1)"; \
        pv="$(ffprobe -version | sed -nE 's/^ffprobe version n?([0-9]+\.[0-9]+(\.[0-9]+)?).*/\1/p' | head -1)"; \
        [ "$(printf '%s\n%s\n' "$FFMPEG_MIN_VERSION" "$fv" | sort -V | head -1)" = "$FFMPEG_MIN_VERSION" ] \
            || { echo "FFmpeg $fv < $FFMPEG_MIN_VERSION (CVE-2026-8461)"; exit 1; }; \
        [ "$(printf '%s\n%s\n' "$FFMPEG_MIN_VERSION" "$pv" | sort -V | head -1)" = "$FFMPEG_MIN_VERSION" ] \
            || { echo "ffprobe $pv < $FFMPEG_MIN_VERSION (CVE-2026-8461)"; exit 1; }; \
        echo "FFmpeg/ffprobe $fv OK (>= $FFMPEG_MIN_VERSION, variant=$FFMPEG_VARIANT)"; \
    else \
        echo "WARNING: FFMPEG_VARIANT=apt may ship FFmpeg < $FFMPEG_MIN_VERSION (CVE-2026-8461); runtime will warn."; \
    fi

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Run as an unprivileged user (defence in depth for untrusted-media processing).
RUN useradd -r -u 10001 -m castcore
USER castcore

CMD ["arq", "app.worker.WorkerSettings"]

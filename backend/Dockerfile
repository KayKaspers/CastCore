# syntax=docker/dockerfile:1

# ── FFmpeg / ffprobe provisioning ────────────────────────────────────────────
# CastCore needs FFmpeg/ffprobe >= 8.1.2 (CVE-2026-8461 / "PixelSmash", MagicYUV decoder).
# The variant is chosen at build time via FFMPEG_VARIANT:
#   copy   (default, recommended) — multi-stage COPY of pinned, static ffmpeg/ffprobe binaries
#   static — download a static tarball and verify its SHA256 (needs URL + SHA256)
#   apt    — Debian's package (may be < 8.1.2; build does NOT gate it, runtime warns)
# For copy/static the build FAILS if the resulting ffmpeg/ffprobe is below FFMPEG_MIN_VERSION.
# Binaries always land in /usr/bin so FFMPEG_PATH stays /usr/bin/ffmpeg for every variant.
ARG FFMPEG_IMAGE=mwader/static-ffmpeg:8.1.2@sha256:33f770f812cbfc3de96c547157fc9faf8bd95a36481753439ffa761045167585
ARG FFMPEG_VARIANT=copy
ARG FFMPEG_MIN_VERSION=8.1.2

# copy: stage the pinned static binaries (/ffmpeg, /ffprobe) under /out
FROM ${FFMPEG_IMAGE} AS ff_copy_bin
FROM python:3.12-slim-trixie AS ff_copy
COPY --from=ff_copy_bin /ffmpeg /ffprobe /out/

# static: download + checksum-verify a static tarball, stage under /out
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

# apt: no static binaries staged (ffmpeg installed via apt in the final image)
FROM python:3.12-slim-trixie AS ff_apt
RUN install -d /out

# select the source stage by variant (only the chosen stage is built)
FROM ff_${FFMPEG_VARIANT} AS ffsrc

# ── Final image ──────────────────────────────────────────────────────────────
# FFmpeg + ffprobe and mount tooling live here so preflight/ffprobe and (optional) in-container
# mounts work. The Process Manager image is the one that spawns long-running stream processes.
FROM python:3.12-slim-trixie
ARG FFMPEG_VARIANT=copy
ARG FFMPEG_MIN_VERSION=8.1.2

COPY --from=ffsrc /out/ /tmp/ffsrc/
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends cifs-utils nfs-common rclone curl; \
    if [ "$FFMPEG_VARIANT" = "apt" ]; then \
        apt-get install -y --no-install-recommends ffmpeg; \
    else \
        install -m755 /tmp/ffsrc/ffmpeg /tmp/ffsrc/ffprobe /usr/bin/; \
    fi; \
    rm -rf /tmp/ffsrc /var/lib/apt/lists/*; \
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
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]

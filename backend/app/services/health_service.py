"""Stream health score (0–100) derived from live process metrics.

Aggregates per-output FFmpeg process metrics (state, encoding speed, reconnects, dropped
frames, throughput) into a per-output and per-job score with a traffic-light status
(green/yellow/red/gray). Optional preflight/readiness levels can be folded in. The output
contains only derived numbers and translatable reason codes — never secrets or stream keys.

Reason codes are returned bare (e.g. ``encoding_speed_low``); the UI prefixes them with
``health.reason.``.
"""

from __future__ import annotations

from typing import Any

GREEN_MIN = 85
YELLOW_MIN = 60


def _reason(code: str, level: str, **params: Any) -> dict:
    return {"code": code, "level": level, "params": params}


def _status_from_score(score: int) -> str:
    if score >= GREEN_MIN:
        return "green"
    if score >= YELLOW_MIN:
        return "yellow"
    return "red"


def output_health(metrics: dict) -> dict:
    """Health of a single output from its process metrics.

    ``metrics`` keys: state, speed, reconnect_count, dropped_frames, fps, bitrate_kbps.
    Returns ``{score, status, reasons}`` (score is None when not running).
    """
    state = metrics.get("state")
    if state == "failed":
        return {"score": 0, "status": "red", "reasons": [_reason("output_failed", "error")]}
    if state in (None, "stopped"):
        return {"score": None, "status": "gray", "reasons": [_reason("not_running", "info")]}
    if state == "starting":
        return {"score": 80, "status": "yellow", "reasons": [_reason("starting", "warn")]}

    # running
    reasons: list[dict] = []
    score = 100
    speed = metrics.get("speed")
    if speed is not None:
        if speed < 0.85:
            score -= 40
            reasons.append(_reason("encoding_speed_critical", "error", speed=round(speed, 2)))
        elif speed < 0.97:
            score -= 18
            reasons.append(_reason("encoding_speed_low", "warn", speed=round(speed, 2)))

    reconnects = metrics.get("reconnect_count") or 0
    if reconnects:
        score -= min(35, reconnects * 12)
        reasons.append(_reason("reconnects", "error" if reconnects >= 3 else "warn", count=reconnects))

    dropped = metrics.get("dropped_frames") or 0
    if dropped:
        score -= 12
        reasons.append(_reason("dropped_frames", "warn", frames=dropped))

    if not metrics.get("fps") or not metrics.get("bitrate_kbps"):
        score -= 12
        reasons.append(_reason("no_throughput", "warn"))

    score = max(0, min(100, score))
    status = _status_from_score(score)
    if not reasons:
        reasons.append(_reason("healthy", "ok"))
    return {"score": score, "status": status, "reasons": reasons}


def compute_job_health(
    job_id: str,
    name: str,
    outputs: list[dict],
    *,
    preflight_level: str | None = None,
    readiness_level: str | None = None,
) -> dict:
    """Aggregate output healths into a job health (weakest running output drives the score)."""
    out_healths = []
    for o in outputs:
        h = output_health(o)
        h = {"output_id": o.get("output_id"), **h}
        out_healths.append(h)

    running = [h for h in out_healths if h["score"] is not None]
    reasons: list[dict] = []
    if not running:
        score: int | None = None
        status = "gray"
        reasons.append(_reason("not_running", "info"))
    else:
        score = min(h["score"] for h in running)
        status = "red" if any(h["status"] == "red" for h in running) else _status_from_score(score)
        seen = set()
        for h in running:
            for r in h["reasons"]:
                if r["code"] != "healthy" and r["code"] not in seen:
                    seen.add(r["code"])
                    reasons.append(r)
        if not reasons:
            reasons.append(_reason("healthy", "ok"))

    # fold optional preflight / readiness levels (None = not checked, no penalty)
    for src, level in (("preflight", preflight_level), ("readiness", readiness_level)):
        if level in ("red", "error"):
            status = "red"
            reasons.append(_reason(f"{src}_failed", "error"))
        elif level in ("yellow", "warn") and status == "green":
            status = "yellow"
            reasons.append(_reason(f"{src}_warning", "warn"))

    return {
        "job_id": job_id,
        "name": name,
        "score": score,
        "status": status,
        "reasons": reasons,
        "outputs": out_healths,
    }

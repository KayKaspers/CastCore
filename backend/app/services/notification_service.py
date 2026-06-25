"""Notification dispatch: webhook / Discord / Slack / Gotify / Telegram / email.

Connection secrets live in the encrypted ``Notification.secret`` (a JSON blob), never
returned by the API and never logged. Sends are best-effort with short timeouts.
"""

from __future__ import annotations

import asyncio
import json
import smtplib
from email.message import EmailMessage

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_secret
from app.models.notification import Notification

EVENTS = [
    "stream_started", "stream_stopped", "stream_failed",
    "source_offline", "preflight_failed", "backup_done", "test",
]

_TIMEOUT = 8.0


def _secret(notif: Notification) -> dict:
    if not notif.secret:
        return {}
    try:
        return json.loads(decrypt_secret(notif.secret))
    except Exception:  # pragma: no cover - defensive
        return {}


async def _send(notif: Notification, title: str, message: str) -> tuple[bool, str | None]:
    s = _secret(notif)
    ch = notif.channel
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            if ch == "discord":
                await client.post(s["url"], json={"content": f"**{title}**\n{message}"})
            elif ch == "slack":
                await client.post(s["url"], json={"text": f"*{title}*\n{message}"})
            elif ch == "gotify":
                await client.post(
                    f"{s['url'].rstrip('/')}/message?token={s['token']}",
                    json={"title": title, "message": message, "priority": 5},
                )
            elif ch == "telegram":
                await client.post(
                    f"https://api.telegram.org/bot{s['bot_token']}/sendMessage",
                    json={"chat_id": s["chat_id"], "text": f"{title}\n{message}"},
                )
            elif ch == "webhook":
                await client.post(s["url"], json={"title": title, "message": message})
            elif ch == "email":
                await asyncio.get_running_loop().run_in_executor(None, _send_email, s, title, message)
            else:
                return False, f"unknown channel: {ch}"
        return True, None
    except KeyError as exc:
        return False, f"missing config field: {exc}"
    except Exception as exc:  # noqa: BLE001 - report any send failure
        return False, str(exc)[:200]


def _send_email(s: dict, title: str, message: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = title
    msg["From"] = s["from"]
    msg["To"] = s["to"]
    msg.set_content(message)
    port = int(s.get("port", 587))
    with smtplib.SMTP(s["host"], port, timeout=_TIMEOUT) as server:
        if s.get("tls", True):
            server.starttls()
        if s.get("username"):
            server.login(s["username"], s.get("password", ""))
        server.send_message(msg)


def _format(event: str, ctx: dict) -> tuple[str, str]:
    name = ctx.get("job_name") or ctx.get("name") or ctx.get("job_id", "")
    titles = {
        "stream_started": f"▶ Stream gestartet: {name}",
        "stream_stopped": f"⏹ Stream gestoppt: {name}",
        "stream_failed": f"⚠ Stream fehlgeschlagen: {name}",
        "source_offline": f"⚠ Quelle offline: {name}",
        "preflight_failed": f"⚠ Preflight fehlgeschlagen: {name}",
        "backup_done": "✔ Backup erstellt",
        "test": "CastCore Test-Benachrichtigung",
    }
    title = titles.get(event, f"CastCore: {event}")
    detail = ctx.get("detail") or ""
    return title, f"{event} {detail}".strip()


async def send_one(notif: Notification, event: str, ctx: dict) -> tuple[bool, str | None]:
    title, message = _format(event, ctx)
    return await _send(notif, title, message)


async def dispatch(db: AsyncSession, event: str, ctx: dict) -> None:
    """Fire an event to all enabled notifications subscribed to it (best-effort)."""
    res = await db.execute(select(Notification).where(Notification.enabled.is_(True)))
    for notif in res.scalars().all():
        if event in (notif.events or []):
            await send_one(notif, event, ctx)

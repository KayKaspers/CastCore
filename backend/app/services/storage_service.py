"""Storage-source logic: local folders + SMB shares (test / mount / browse).

Security:
- SMB passwords encrypted at rest (Fernet); written only to a 0600 credentials file,
  never passed on the command line (would show in process listings) or logged.
- All external commands run via argument lists (shell=False).
- Browsing is confined to the source's effective path (no path traversal).
"""

from __future__ import annotations

import asyncio
import datetime as dt
import os
import stat
from pathlib import Path

from app.core.config import get_settings
from app.core.security import decrypt_secret
from app.models.storage import SmbSource, StorageSource

_MEDIA_EXT = {".mp4", ".mkv", ".mov", ".avi", ".ts", ".m2ts", ".flv", ".webm",
              ".mp3", ".aac", ".wav", ".m4a", ".m3u8", ".jpg", ".png"}
_BROWSE_LIMIT = 500


def effective_path(source: StorageSource) -> str | None:
    if source.type == "smb" and source.smb is not None:
        return source.smb.mount_path
    return source.path


def _confine(base: str, subpath: str) -> Path:
    """Resolve base/subpath, ensuring the result stays within base (no traversal)."""
    base_p = Path(base).resolve()
    target = (base_p / subpath.lstrip("/")).resolve()
    if base_p != target and base_p not in target.parents:
        raise ValueError("path traversal blocked")
    return target


async def test_source(source: StorageSource) -> tuple[bool, str | None]:
    """Lightweight reachability test. Local: path readable. SMB: TCP connect to 445."""
    if source.type == "smb" and source.smb is not None:
        try:
            fut = asyncio.open_connection(source.smb.server, 445)
            reader, writer = await asyncio.wait_for(fut, timeout=5)
            writer.close()
            await writer.wait_closed()
            return True, None
        except (OSError, asyncio.TimeoutError) as exc:
            return False, f"{source.smb.server}:445 unreachable ({exc})"
    path = source.path
    if not path:
        return False, "no path configured"
    if os.path.isdir(path) and os.access(path, os.R_OK):
        return True, None
    return False, f"{path} not readable"


async def mount_smb(source: StorageSource) -> tuple[bool, str | None]:
    """Mount an SMB share via mount.cifs using a secure credentials file.

    Requires privileges (root + CAP_SYS_ADMIN). In the default unprivileged container
    this fails by design — prefer mounting on the host and bind-mounting the path
    (see docs/DEPLOYMENT.md). Works on native installs and privileged containers.
    """
    smb: SmbSource | None = source.smb
    if smb is None:
        return False, "not an SMB source"

    os.makedirs(smb.mount_path, exist_ok=True)

    # Credentials file (0600) — keeps the password out of the process command line.
    settings = get_settings()
    cred_dir = Path(settings.data_dir) / "smbcreds"
    cred_dir.mkdir(parents=True, exist_ok=True)
    cred_file = cred_dir / f"{source.id}.cred"
    lines = [f"username={smb.username or ''}", f"password={decrypt_secret(smb.password) if smb.password else ''}"]
    if smb.domain:
        lines.append(f"domain={smb.domain}")
    cred_file.write_text("\n".join(lines) + "\n")
    os.chmod(cred_file, stat.S_IRUSR | stat.S_IWUSR)  # 0600

    options = [f"credentials={cred_file}", "iocharset=utf8"]
    options.append("ro" if source.read_only else "rw")
    if smb.smb_version:
        options.append(f"vers={smb.smb_version}")
    unc = f"//{smb.server}/{smb.share}"
    args = ["mount", "-t", "cifs", unc, smb.mount_path, "-o", ",".join(options)]

    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, err = await asyncio.wait_for(proc.communicate(), timeout=20)
    except (OSError, asyncio.TimeoutError) as exc:
        return False, str(exc)
    if proc.returncode != 0:
        # Do not leak the credentials path content; mount.cifs errors are safe to show.
        return False, err.decode("utf-8", "replace").strip()[:300] or "mount failed"
    return True, None


async def unmount(source: StorageSource) -> tuple[bool, str | None]:
    path = effective_path(source)
    if not path:
        return False, "no mount path"
    try:
        proc = await asyncio.create_subprocess_exec(
            "umount", path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, err = await asyncio.wait_for(proc.communicate(), timeout=15)
    except (OSError, asyncio.TimeoutError) as exc:
        return False, str(exc)
    if proc.returncode != 0:
        return False, err.decode("utf-8", "replace").strip()[:300] or "umount failed"
    return True, None


def browse(source: StorageSource, subpath: str = "") -> list[dict]:
    """List directory entries under the source path (confined, media-aware)."""
    base = effective_path(source)
    if not base:
        raise ValueError("source has no path")
    target = _confine(base, subpath)
    if not target.is_dir():
        raise ValueError("not a directory")

    entries: list[dict] = []
    for entry in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if len(entries) >= _BROWSE_LIMIT:
            break
        is_dir = entry.is_dir()
        ext = entry.suffix.lower()
        try:
            size = entry.stat().st_size if not is_dir else 0
        except OSError:
            size = 0
        entries.append({
            "name": entry.name,
            "rel_path": str(entry.relative_to(Path(base).resolve())),
            "abs_path": str(entry),
            "is_dir": is_dir,
            "size": size,
            "streamable": (not is_dir) and ext in _MEDIA_EXT,
        })
    return entries


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

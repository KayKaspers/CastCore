#!/usr/bin/env sh
# Backend container entrypoint: wait for Postgres, run migrations, then serve.
# Only the backend service runs migrations (single migrator); worker/process-manager
# just wait for the schema via the app.
set -e

echo "[castcore] waiting for database…"
python - <<'PY'
import os, time, socket
host = os.getenv("POSTGRES_HOST", "postgres")
port = int(os.getenv("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("[castcore] database not reachable")
print("[castcore] database is up")
PY

echo "[castcore] running migrations (alembic upgrade head)…"
alembic upgrade head

echo "[castcore] starting API…"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

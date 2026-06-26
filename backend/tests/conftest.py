"""Test configuration and shared fixtures.

Unit tests need nothing here. **Integration tests** use a real PostgreSQL test database
(`castcore_test`), isolated from the app/dev database:

- Schema is created once per session via ``Base.metadata.create_all`` (sync engine).
- Each test starts clean: every table is truncated and the default roles re-seeded.
- The app's ``get_db`` dependency is overridden to use the test engine.
- The HTTP layer is exercised in-process via httpx ``ASGITransport`` (no network, and the
  app lifespan — i.e. the Redis status/scheduler loops — is intentionally not started).

Connection comes from the standard ``POSTGRES_*`` env vars; the database name is
``TEST_DB_NAME`` (default ``castcore_test``). Rate limiting is disabled so tests are not
throttled.
"""

from __future__ import annotations

import os

from cryptography.fernet import Fernet

# Must be set before app settings are first read.
os.environ.setdefault("CASTCORE_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

import app.models  # noqa: E402,F401  (registers every model on Base.metadata)
from app.core.security import create_access_token  # noqa: E402
from app.db.base import Base  # noqa: E402

_PG_USER = os.environ.get("POSTGRES_USER", "castcore")
_PG_PW = os.environ.get("POSTGRES_PASSWORD", "castcore")
_PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
_PG_PORT = os.environ.get("POSTGRES_PORT", "5432")
_TEST_DB = os.environ.get("TEST_DB_NAME", "castcore_test")

_SYNC_URL = f"postgresql+psycopg2://{_PG_USER}:{_PG_PW}@{_PG_HOST}:{_PG_PORT}/{_TEST_DB}"
_ASYNC_URL = f"postgresql+asyncpg://{_PG_USER}:{_PG_PW}@{_PG_HOST}:{_PG_PORT}/{_TEST_DB}"

ROLE_PERMS = {
    "admin": {"*": True},
    "operator": {"streams": True, "sources": True, "platforms": True},
    "viewer": {"read": True},
}


def _ensure_database() -> None:
    """Create the test database if it does not exist (idempotent)."""
    import psycopg2
    from psycopg2 import errors

    conn = psycopg2.connect(
        host=_PG_HOST, port=_PG_PORT, user=_PG_USER, password=_PG_PW, dbname="postgres"
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            try:
                cur.execute(f'CREATE DATABASE "{_TEST_DB}"')
            except errors.DuplicateDatabase:
                pass
    finally:
        conn.close()


@pytest.fixture(scope="session")
def _schema() -> None:
    """Create the schema once per test session (sync engine, no event loop)."""
    _ensure_database()
    engine = create_engine(_SYNC_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.dispose()


@pytest_asyncio.fixture
async def db_engine(_schema):  # noqa: ANN001
    engine = create_async_engine(_ASYNC_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine):  # noqa: ANN001
    """Truncate all tables, re-seed roles, and return an async session factory."""
    import uuid

    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    tables = ", ".join(f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables))
    async with factory() as s:
        await s.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
        for name, perms in ROLE_PERMS.items():
            await s.execute(
                text("INSERT INTO roles (id, name, permissions) VALUES (:id, :n, :p)"),
                {"id": uuid.uuid4(), "n": name, "p": __import__("json").dumps(perms)},
            )
        await s.commit()
    return factory


@pytest_asyncio.fixture
async def db(session_factory):  # noqa: ANN001
    """An async session for seeding test data."""
    async with session_factory() as s:
        yield s


@pytest_asyncio.fixture
async def client(session_factory):  # noqa: ANN001
    """httpx client wired to the app with the test DB injected via dependency override."""
    from app.db.session import get_db
    from app.main import app

    async def _override_get_db():
        async with session_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ---- helpers shared across integration tests -------------------------------------------

def _token_for(user) -> str:
    """Mint an access token for a user (roles are enforced from the DB, not the token)."""
    return create_access_token(str(user.id), extra={"roles": user.role_names})


@pytest_asyncio.fixture
async def user_factory(db):  # noqa: ANN001
    """Factory: create a user with one role; returns the ORM user."""
    from app.services.auth_service import create_user

    async def _make(username: str, role: str, *, password: str = "Sup3r!Secret",
                    active: bool = True):
        user = await create_user(
            db, username=username, password=password, email=None, language="de",
            role_names=[role],
        )
        user.is_active = active
        await db.commit()
        return user

    return _make


@pytest_asyncio.fixture
async def roles_tokens(user_factory):  # noqa: ANN001
    """Three users (admin/operator/viewer) with access tokens, ready for RBAC tests."""
    users = {
        "admin": await user_factory("admin_u", "admin"),
        "operator": await user_factory("operator_u", "operator"),
        "viewer": await user_factory("viewer_u", "viewer"),
    }
    return {
        "tokens": {role: _token_for(u) for role, u in users.items()},
        "users": users,
    }


@pytest.fixture
def mint():
    """Return the token-minting helper for ad-hoc use in tests."""
    return _token_for

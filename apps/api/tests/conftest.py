"""
Shared pytest fixtures for the Galley API test suite.

All fixtures use pytest's `tmp_path` to get a unique SQLite file per test
invocation, eliminating the shared-path corruption risk when running tests
in parallel (see CLAUDE.md).

Usage
-----
- `async_client` — HTTP client wired to an isolated DB; use for all HTTP tests
- `db_session`   — direct SQLAlchemy session into the same isolated DB;
                   use only when a test needs to inspect or seed the DB directly
- Both fixtures share the same engine, so HTTP writes are visible to `db_session`
  and vice versa within the same test.

Legacy test files that still define their own db_session/client fixtures are
unaffected — local fixtures always take precedence over conftest fixtures.
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings
from src.db.database import get_db
from src.db.init_db import init_db
from src.main import app


# ── Shared engine ─────────────────────────────────────────────────────────────

@pytest.fixture
def _test_engine(tmp_path):
    """
    Create a migrations-applied SQLite engine for one test.

    Uses pytest's tmp_path (a per-test temporary directory) so parallel
    workers never share the same database file.
    """
    db_url = f"sqlite:///{tmp_path}/galley_test.sqlite"
    db_path = str(tmp_path / "galley_test.sqlite")

    orig_url = settings.database_url
    settings.database_url = db_url
    init_db()
    settings.database_url = orig_url

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


# ── Public fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def db_session(_test_engine):
    """
    Direct SQLAlchemy session into the test's isolated DB.

    Shares the same engine as `async_client`, so writes made via HTTP are
    visible here (and vice versa) within the same test.
    """
    Session = sessionmaker(bind=_test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
async def async_client(_test_engine):
    """
    An httpx AsyncClient wired to an isolated test database.

    Usage::

        async def test_something(async_client):
            response = await async_client.get("/api/v1/recipes")
            assert response.status_code == 200
    """
    Session = sessionmaker(bind=_test_engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)

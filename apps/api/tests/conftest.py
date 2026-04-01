"""
Shared pytest fixtures for the Galley API test suite.

Existing test files manage their own DB fixtures and are unaffected by this
file — local fixtures always take precedence over conftest fixtures.

New tests should use `async_client` from here rather than hand-rolling the
DB setup, which eliminates the shared-path corruption risk when multiple
pytest workers run simultaneously.

Parallel safety
---------------
Each `async_client` fixture call gets a unique SQLite path via pytest's
`tmp_path` fixture, so concurrent test workers never share a DB file.
The CLAUDE.md warning ("parallel pytest runs corrupt the test DB") applies
only to test files that still use the old fixed path `./data/db/galley_test.sqlite`.
"""

import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings
from src.db.database import Base, get_db
from src.db.init_db import init_db
from src.main import app


@pytest.fixture
def tmp_test_db_url(tmp_path):
    """
    Unique SQLite URL for this test invocation.

    Uses pytest's tmp_path (a per-test temporary directory) so parallel
    workers never share the same database file.
    """
    return f"sqlite:///{tmp_path}/galley_test.sqlite"


@pytest.fixture
async def async_client(tmp_test_db_url):
    """
    An httpx AsyncClient wired to an isolated test database.

    Usage::

        async def test_something(async_client):
            response = await async_client.get("/api/v1/recipes")
            assert response.status_code == 200
    """
    db_path = tmp_test_db_url.replace("sqlite:///", "")

    # Run migrations against the isolated test DB
    orig_url = settings.database_url
    settings.database_url = tmp_test_db_url
    init_db()
    settings.database_url = orig_url

    engine = create_engine(tmp_test_db_url, connect_args={"check_same_thread": False})
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
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
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)

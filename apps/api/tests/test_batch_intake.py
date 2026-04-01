"""
Tests for POST /api/v1/intake-jobs/batch — batch intake creation.
"""
import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.anyio


async def test_batch_create_two_jobs(async_client: AsyncClient):
    payload = {
        "jobs": [
            {"intake_type": "paste_text", "raw_source_text": "Recipe A text"},
            {"intake_type": "paste_text", "raw_source_text": "Recipe B text"},
        ]
    }
    resp = await async_client.post("/api/v1/intake-jobs/batch", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["total"] == 2
    assert data["succeeded"] == 2
    assert data["failed"] == 0
    assert len(data["created"]) == 2
    assert data["errors"] == []
    for job in data["created"]:
        assert "id" in job
        assert job["intake_type"] == "paste_text"
        assert job["status"] == "captured"


async def test_batch_create_partial_failure(async_client: AsyncClient):
    """A paste_text job missing raw_source_text fails; others succeed."""
    payload = {
        "jobs": [
            {"intake_type": "paste_text", "raw_source_text": "Good recipe"},
            {"intake_type": "paste_text"},  # missing raw_source_text — will fail
        ]
    }
    resp = await async_client.post("/api/v1/intake-jobs/batch", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["total"] == 2
    assert data["succeeded"] == 1
    assert data["failed"] == 1
    assert len(data["created"]) == 1
    assert len(data["errors"]) == 1
    assert data["errors"][0]["index"] == 1


async def test_batch_create_manual_job(async_client: AsyncClient):
    payload = {
        "jobs": [
            {"intake_type": "manual"},
        ]
    }
    resp = await async_client.post("/api/v1/intake-jobs/batch", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["succeeded"] == 1
    assert data["created"][0]["intake_type"] == "manual"


async def test_batch_empty_list_rejected(async_client: AsyncClient):
    """Empty jobs list is rejected (min_length=1)."""
    payload = {"jobs": []}
    resp = await async_client.post("/api/v1/intake-jobs/batch", json=payload)
    assert resp.status_code == 422

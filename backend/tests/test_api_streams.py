"""API integration tests: stream-job CRUD, FFmpeg command preview, preflight."""

from __future__ import annotations

import pytest

V1 = "/api/v1"


@pytest.fixture
def op_headers(roles_tokens):
    return {"authorization": f"Bearer {roles_tokens['tokens']['operator']}"}


async def _make_profile_and_destination(client, headers) -> tuple[str, str]:
    r = await client.post(
        f"{V1}/ffmpeg-profiles",
        headers=headers,
        json={"name": "copy", "copy_mode": True},
    )
    assert r.status_code in (200, 201), r.text
    profile_id = r.json()["id"]

    r = await client.post(
        f"{V1}/destinations",
        headers=headers,
        json={"name": "Twitch", "kind": "rtmp", "url": "rtmp://live/app", "stream_key": "SECRET_KEY_42"},
    )
    assert r.status_code in (200, 201), r.text
    dest_id = r.json()["id"]
    return profile_id, dest_id


async def test_stream_job_crud(client, op_headers):
    profile_id, dest_id = await _make_profile_and_destination(client, op_headers)

    create = {
        "name": "My stream",
        "ffmpeg_profile_id": profile_id,
        "inputs": [{"kind": "file", "uri": "/data/media/clip.mp4"}],
        "outputs": [{"format": "flv", "destination_id": dest_id}],
    }
    r = await client.post(f"{V1}/stream-jobs", headers=op_headers, json=create)
    assert r.status_code == 201, r.text
    job_id = r.json()["id"]
    assert r.json()["name"] == "My stream"

    r = await client.get(f"{V1}/stream-jobs", headers=op_headers)
    assert r.status_code == 200 and any(j["id"] == job_id for j in r.json())

    r = await client.get(f"{V1}/stream-jobs/{job_id}", headers=op_headers)
    assert r.status_code == 200 and r.json()["id"] == job_id

    r = await client.delete(f"{V1}/stream-jobs/{job_id}", headers=op_headers)
    assert r.status_code == 204
    r = await client.get(f"{V1}/stream-jobs/{job_id}", headers=op_headers)
    assert r.status_code == 404


async def test_command_preview_masks_stream_key(client, op_headers):
    profile_id, dest_id = await _make_profile_and_destination(client, op_headers)
    create = {
        "name": "Preview job",
        "ffmpeg_profile_id": profile_id,
        "inputs": [{"kind": "file", "uri": "/data/media/clip.mp4"}],
        "outputs": [{"format": "flv", "destination_id": dest_id}],
    }
    job_id = (await client.post(f"{V1}/stream-jobs", headers=op_headers, json=create)).json()["id"]

    r = await client.post(f"{V1}/stream-jobs/{job_id}/preview", headers=op_headers)
    assert r.status_code == 200, r.text
    previews = r.json()["previews"]
    assert len(previews) == 1
    cmd = next(iter(previews.values()))
    assert "ffmpeg" in cmd and "rtmp://live/app" in cmd
    # the raw stream key must never appear in the preview (it is masked)
    assert "SECRET_KEY_42" not in cmd


async def test_preflight_returns_report(client, op_headers):
    profile_id, dest_id = await _make_profile_and_destination(client, op_headers)
    create = {
        "name": "Preflight job",
        "ffmpeg_profile_id": profile_id,
        "inputs": [{"kind": "file", "uri": "/data/media/does-not-exist.mp4"}],
        "outputs": [{"format": "flv", "destination_id": dest_id}],
    }
    job_id = (await client.post(f"{V1}/stream-jobs", headers=op_headers, json=create)).json()["id"]

    r = await client.post(f"{V1}/stream-jobs/{job_id}/preflight", headers=op_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["level"] in ("green", "yellow", "red")
    assert isinstance(body["checks"], list) and body["checks"]

"""End-to-End-Smoke-Test mit Fake-Pipeline: Ingest-PCM rein, Caption+Audio beim Hörer raus."""
import math
import os
import struct

os.environ["NEX26_FAKE_PIPELINE"] = "1"
os.environ["NEX26_INGEST_TOKEN"] = "test-token"

from fastapi.testclient import TestClient  # noqa: E402

from server.main import app  # noqa: E402


def tone(seconds: float, rate: int = 16000) -> bytes:
    n = int(seconds * rate)
    return b"".join(struct.pack("<h", int(6000 * math.sin(2 * math.pi * 300 * i / rate))) for i in range(n))


def test_health_and_pages():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert "Live-Übersetzung" in client.get("/").text
        assert client.get("/stage").status_code == 403
        assert client.get("/stage?token=test-token").status_code == 200


def test_ingest_requires_token():
    import pytest
    from starlette.websockets import WebSocketDisconnect

    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws/ingest?token=wrong") as ws:
                ws.receive_text()


def test_pipeline_end_to_end():
    audio = tone(2.0) + b"\x00\x00" * 16000 + tone(1.0) + b"\x00\x00" * 16000
    with TestClient(app) as client:
        with client.websocket_connect("/ws/listen") as listener:
            with client.websocket_connect("/ws/ingest?token=test-token") as ingest:
                for i in range(0, len(audio), 3200):
                    ingest.send_bytes(audio[i:i + 3200])
                caption = listener.receive_json()
                assert caption["type"] == "caption"
                assert caption["de"].startswith("[DE]")
                audio_msg = listener.receive_bytes()
                assert len(audio_msg) > 100

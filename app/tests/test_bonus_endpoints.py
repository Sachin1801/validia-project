import base64
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils import face_analyzer as fa
import app.api.v1.bonus_endpoints as be

client = TestClient(app)

# Generate a minimal valid 1×1 JPEG via Pillow to ensure OpenCV can decode it
try:
    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (1, 1), color=(0, 0, 0)).save(buffer, format="JPEG")
    MINIMAL_JPG = buffer.getvalue()
except ModuleNotFoundError:
    # Fallback to a small hard-coded JPEG header + pixel if Pillow missing
    MINIMAL_JPG = base64.b64decode(
        b"/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////\n/2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFwABAQEBAAAAAAAAAAAAAAAAAAIEBf/EABYBAQEBAAAAAAAAAAAAAAAAAAABAv/aAAwDAQACEAMQAAAAp//EABcQAQEBAQAAAAAAAAAAAAAAAAEAERL/2gAIAQEAAT8AQ0P/xAAWEQEBAQAAAAAAAAAAAAAAAAAAARH/2gAIAQIBAT8AN//EABYRAQEBAAAAAAAAAAAAAAAAABEAIf/aAAgBAwEBPwBX/9k="
    )


def test_verify_face_empty():
    res = client.post(
        "/v1/verify-face", files={"file": ("", b"", "application/octet-stream")}
    )
    assert res.status_code == 422  # FastAPI validation error for empty upload


def test_detect_deepfake_stub():
    res = client.post(
        "/v1/detect-deepfake", files={"file": ("img.jpg", MINIMAL_JPG, "image/jpeg")}
    )
    assert res.status_code == 200
    data = res.json()
    assert 0 <= data["confidence"] <= 1
    assert isinstance(data["is_deepfake"], bool)


# --------- new profile identification tests ----------


def dummy_profile():
    return {
        "landmarks": [(i, i) for i in range(68)],
        "eye_distance": 100.0,
        "yaw": 0.0,
    }


def test_identify_matching(monkeypatch):
    # Monkeypatch analyze_face to return deterministic profile
    fake = lambda _bytes: dummy_profile()
    monkeypatch.setattr(fa, "analyze_face", fake)
    monkeypatch.setattr(be, "analyze_face", fake)

    # store profile
    res = client.post(
        "/v1/store-profile", files={"file": ("img.jpg", b"stub", "image/jpeg")}
    )
    assert res.status_code == 200
    pid = res.json()["id"]

    # identify with another image (same dummy)
    res2 = client.post(
        f"/v1/identify-face?profile_id={pid}",
        files={"file": ("img2.jpg", b"stub2", "image/jpeg")},
    )
    assert res2.status_code == 200
    out = res2.json()
    assert out["is_match"] is True

import base64
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app

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

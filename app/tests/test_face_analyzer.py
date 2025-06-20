import pytest

from app.utils.face_analyzer import analyze_face, MODEL_PATH


def test_analyze_face_invalid_bytes():
    # Passing random bytes that are not a valid image should raise ValueError
    with pytest.raises(ValueError):
        analyze_face(b"not an image")


def test_analyze_face_missing_model(monkeypatch, tmp_path):
    """If the model file is missing, analyze_face should raise RuntimeError."""
    # Temporarily ensure model path points to non-existent file
    monkeypatch.setattr(
        "app.utils.face_analyzer.MODEL_PATH", str(tmp_path / "missing.dat")
    )

    # Generate a minimal valid 1x1 JPEG image in-memory so OpenCV can decode it
    from io import BytesIO
    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (1, 1), color=(0, 0, 0)).save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    with pytest.raises(RuntimeError):
        analyze_face(img_bytes)

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

    # Use a 1x1 PNG black pixel as minimal valid image bytes
    import base64

    img_bytes = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )

    with pytest.raises(RuntimeError):
        analyze_face(img_bytes)

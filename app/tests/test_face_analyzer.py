import pytest

from app.utils.face_analyzer import analyze_face


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

    # Create a 64×64 random noise image with acceptable brightness so quality gate passes
    import numpy as np
    import cv2

    rng = np.random.default_rng(42)
    noise = rng.integers(low=80, high=170, size=(64, 64, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", noise)
    img_bytes = encoded.tobytes()

    with pytest.raises(RuntimeError):
        analyze_face(img_bytes)


def test_quality_gate_too_dark():
    """A completely black image should trigger brightness ValueError."""
    import numpy as np
    import cv2

    dark = np.zeros((32, 32, 3), dtype=np.uint8)
    _, enc = cv2.imencode(".jpg", dark)
    with pytest.raises(ValueError):
        analyze_face(enc.tobytes())


def test_quality_gate_blurry():
    """Uniform gray image should fail Laplacian variance check."""
    import numpy as np
    import cv2

    grey = np.full((32, 32, 3), 120, dtype=np.uint8)
    _, enc = cv2.imencode(".jpg", grey)
    with pytest.raises(ValueError):
        analyze_face(enc.tobytes())

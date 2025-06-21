from typing import Dict, List, Tuple

import cv2
import dlib
import numpy as np
import base64

# Initialize dlib's detector and predictor only once (lazy load predictor because model file is large)
_detector = dlib.get_frontal_face_detector()
_predictor = None  # type: ignore

# Path to the pretrained model (user must download manually)
MODEL_PATH = "models/shape_predictor_68_face_landmarks.dat"

# Thresholds for image-quality gating
BRIGHTNESS_MIN = 60
BRIGHTNESS_MAX = 200
LAPLACIAN_VAR_MIN = 100.0


def _load_predictor() -> dlib.shape_predictor:
    """Load the shape predictor lazily to avoid startup overhead."""
    global _predictor
    if _predictor is None:
        try:
            _predictor = dlib.shape_predictor(MODEL_PATH)
        except RuntimeError as err:
            raise RuntimeError(
                f"Unable to load facial landmark model at '{MODEL_PATH}'. "
                "Download it from https://github.com/davisking/dlib-models and place it under 'models/'."
            ) from err
    return _predictor


def analyze_face(image_bytes: bytes) -> Dict[str, any]:
    """Analyze a face in the given image bytes and return simple metrics.

    Raises:
        ValueError: If no face is detected.
        RuntimeError: If the predictor model cannot be loaded.
    """
    # Convert bytes to numpy array & decode image first
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Provided bytes do not represent a valid image")

    # Image quality gate — brightness & sharpness heuristics
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    brightness = float(np.mean(gray))
    if brightness < BRIGHTNESS_MIN or brightness > BRIGHTNESS_MAX:
        raise ValueError(
            f"Image brightness {brightness:.1f} outside acceptable range {BRIGHTNESS_MIN}-{BRIGHTNESS_MAX}."
        )

    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if lap_var < LAPLACIAN_VAR_MIN:
        raise ValueError(
            f"Image too blurry (variance of Laplacian {lap_var:.1f} < {LAPLACIAN_VAR_MIN})."
        )

    # Ensure landmark predictor can be loaded (raises RuntimeError if missing)
    predictor = _load_predictor()

    # Detect faces
    rects = _detector(gray, 1)
    if not rects:
        raise ValueError("No face detected in the image")

    # Use the first detected face
    rect = rects[0]
    shape = predictor(gray, rect)
    landmarks: List[Tuple[int, int]] = [(pt.x, pt.y) for pt in shape.parts()]

    # Example metric: eye distance between outer eye corners
    left_eye = landmarks[36]  # landmark 37 in 1-indexed spec
    right_eye = landmarks[45]  # landmark 46
    eye_distance = float(np.linalg.norm(np.subtract(left_eye, right_eye)))

    # Placeholder values for yaw (head pose) until implemented
    yaw = 0.0

    # Aligned 150×150 face chip
    chip_img = dlib.get_face_chip(img, shape, size=150)
    # Encode chip to JPEG base64
    success, buf = cv2.imencode(".jpg", chip_img)
    if not success:
        raise RuntimeError("Failed to encode aligned face chip")
    aligned_face_b64 = base64.b64encode(buf.tobytes()).decode("ascii")

    return {
        "landmarks": landmarks,
        "eye_distance": eye_distance,
        "yaw": yaw,
        "aligned_face": aligned_face_b64,
        "_chip": chip_img,  # internal use (not serialised in API)
    }

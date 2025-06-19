from typing import Dict, List, Tuple

import cv2
import dlib
import numpy as np

# Initialize dlib's detector and predictor only once (lazy load predictor because model file is large)
_detector = dlib.get_frontal_face_detector()
_predictor = None  # type: ignore

# Path to the pretrained model (user must download manually)
MODEL_PATH = "models/shape_predictor_68_face_landmarks.dat"


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
    # Convert bytes to numpy array & decode image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Provided bytes do not represent a valid image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    rects = _detector(gray, 1)
    if not rects:
        raise ValueError("No face detected in the image")

    # Use the first detected face
    rect = rects[0]
    predictor = _load_predictor()
    shape = predictor(gray, rect)
    landmarks: List[Tuple[int, int]] = [(pt.x, pt.y) for pt in shape.parts()]

    # Example metric: eye distance between outer eye corners
    left_eye = landmarks[36]  # landmark 37 in 1-indexed spec
    right_eye = landmarks[45]  # landmark 46
    eye_distance = float(np.linalg.norm(np.subtract(left_eye, right_eye)))

    # Placeholder values for yaw (head pose) until implemented
    yaw = 0.0

    return {
        "landmarks": landmarks,
        "eye_distance": eye_distance,
        "yaw": yaw,
    }

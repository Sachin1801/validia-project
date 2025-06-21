from fastapi import APIRouter, File, UploadFile, HTTPException

import cv2
import numpy as np

from app.utils.face_analyzer import analyze_face
from app.models.profile import Profile
from app.models.deepfake import DeepfakeResult

router = APIRouter(tags=["bonus"])


@router.post(
    "/verify-face",
    response_model=Profile,
    summary="Verify face authenticity",
    description="Generates a facial profile and performs basic liveness checks (stub).",
    responses={
        400: {
            "description": "Bad request – invalid image data or no face detected",
            "content": {
                "application/json": {
                    "example": {"detail": "No face detected in the image"}
                }
            },
        },
        422: {"description": "Validation error – file not provided"},
    },
)
async def verify_face(file: UploadFile = File(...)) -> Profile:  # noqa: D401
    """Upload an image and return a facial profile with a liveness placeholder."""
    content = await file.read()

    try:
        data = analyze_face(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Placeholder liveness check (always passes)
    description = (
        f"Face OK. Eye distance: {data['eye_distance']:.1f}px and yaw {data['yaw']:.1f}. "
        "(Liveness check: stub, always passes)"
    )

    return Profile(**data, description=description)


@router.post(
    "/detect-deepfake",
    response_model=DeepfakeResult,
    summary="Detect possible deepfakes (stub)",
    description="Returns a dummy deepfake confidence score between 0 and 1.",
    responses={
        400: {
            "description": "Bad request – invalid image data",
            "content": {
                "application/json": {"example": {"detail": "Invalid image data"}}
            },
        },
        422: {"description": "Validation error – file not provided"},
    },
)
async def detect_deepfake(file: UploadFile = File(...)) -> DeepfakeResult:  # noqa: D401
    """Upload an image/video frame and return a stub deepfake prediction."""
    content = await file.read()

    # Simple decode to verify image validity; errors propagate as 400s
    np_arr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # Stub: deterministic pseudo-confidence using hash of bytes for consistency
    pseudo_val = (hash(content) % 100) / 100  # 0–0.99
    confidence = float(round(pseudo_val, 2))
    is_fake = confidence > 0.5
    desc = "Deepfake suspected" if is_fake else "Likely genuine"

    return DeepfakeResult(is_deepfake=is_fake, confidence=confidence, description=desc)

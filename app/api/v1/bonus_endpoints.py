from fastapi import APIRouter, File, UploadFile, HTTPException

import cv2
import numpy as np

from app.utils.face_analyzer import analyze_face
from app.models.profile import Profile
from app.models.deepfake import DeepfakeResult
from app.utils.profile_store import profile_store
from app.utils.face_compare import compare_profiles

router = APIRouter(tags=["bonus"])
THRESHOLD = 0.60

THRESH_SIMILARITY = 0.1  # tune later


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

    return Profile(
        landmarks=data["landmarks"],
        eye_distance=data["eye_distance"],
        yaw=data["yaw"],
        description=description,
        aligned_face=data.get("aligned_face"),
    )


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
    is_fake = confidence > THRESHOLD
    desc = "Deepfake suspected" if is_fake else "Likely genuine"

    return DeepfakeResult(is_deepfake=is_fake, confidence=confidence, description=desc)


class IdentifyResult(DeepfakeResult):  # reuse structure but different semantics
    is_match: bool


@router.post(
    "/store-profile",
    response_model=Profile,
    summary="Store a facial profile and return its id",
    description="Creates a profile from an uploaded image and saves it in memory for later matching.",
)
async def store_profile(file: UploadFile = File(...)) -> Profile:  # noqa: D401
    content = await file.read()
    data = analyze_face(content)

    # Generate 5 jittered crops for augmentation
    chip_img = data.get("_chip")
    jitter_faces_b64 = None
    if chip_img is not None:
        try:
            import dlib
            import base64

            jitters = dlib.jitter_image(chip_img, 5)
            encoded = []
            for j in jitters:
                ok, buf = cv2.imencode(".jpg", j)
                if ok:
                    encoded.append(base64.b64encode(buf.tobytes()).decode("ascii"))
            jitter_faces_b64 = encoded or None
        except Exception:
            # Swallow any augmentation errors; continue without
            jitter_faces_b64 = None

    profile = Profile(
        landmarks=data["landmarks"],
        eye_distance=data["eye_distance"],
        yaw=data["yaw"],
        description="Stored profile",
        aligned_face=data.get("aligned_face"),
        jitter_faces=jitter_faces_b64,
    )
    _id = profile_store.add(profile)
    profile.id = _id
    return profile


@router.post(
    "/identify-face",
    summary="Compare an image with a stored profile id and report if it matches",
    responses={
        200: {"description": "Comparison completed"},
        404: {"description": "Profile not found"},
        400: {"description": "Invalid image or no face"},
    },
)
async def identify_face(
    profile_id: str, file: UploadFile = File(...)
) -> dict:  # noqa: D401
    """Return match boolean and distance score."""

    # fetch reference profile
    try:
        ref_profile = profile_store.get(profile_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Reference profile not found")

    # analyze new image
    content = await file.read()
    try:
        probe_data = analyze_face(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _fields = {
        k: probe_data[k]
        for k in (
            "landmarks",
            "eye_distance",
            "yaw",
            "aligned_face",
        )
        if k in probe_data
    }
    probe_profile = Profile(**_fields)
    distance = compare_profiles(ref_profile, probe_profile)
    distance = float(distance)
    is_match = bool(distance < THRESH_SIMILARITY)

    return {
        "is_match": is_match,
        "distance": distance,
        "threshold": THRESH_SIMILARITY,
        "reference_id": profile_id,
    }

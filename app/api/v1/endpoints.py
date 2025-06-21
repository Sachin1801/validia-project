from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.profile import Profile
from app.utils.face_analyzer import analyze_face

router = APIRouter()


@router.get("/ping", summary="Ping")
async def ping():
    """Simple liveness check."""
    return {"ping": "pong"}


@router.post(
    "/create-profile",
    response_model=Profile,
    summary="Create facial profile",
    responses={
        400: {
            "description": "Bad request – invalid image bytes or no face detected",
            "content": {
                "application/json": {
                    "example": {"detail": "No face detected in the image"}
                }
            },
        },
        500: {
            "description": "Server error – landmark model missing or cannot be loaded",
            "content": {
                "application/json": {
                    "example": {"detail": "Unable to load facial landmark model"}
                }
            },
        },
    },
)
async def create_profile(file: UploadFile = File(...)) -> Profile:
    """Create a facial profile from an uploaded image."""
    content = await file.read()

    try:
        profile_data = analyze_face(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:  # model missing etc.
        raise HTTPException(status_code=500, detail=str(exc))

    description = f"Detected face with eye distance {profile_data['eye_distance']:.1f}px and yaw {profile_data['yaw']:.1f}."

    return Profile(
        landmarks=profile_data["landmarks"],
        eye_distance=profile_data["eye_distance"],
        yaw=profile_data["yaw"],
        description=description,
        aligned_face=profile_data.get("aligned_face"),
    )


@router.post(
    "/create-profile-extended",
    response_model=Profile,
    summary="Upload an image to generate a creative facial profile",
    description="Returns landmarks, metrics, plus emotion and symmetry scores.",
    responses={
        200: {"description": "Successful creative profile generation"},
        400: {"description": "Invalid input or face not found"},
    },
)
async def create_profile_extended(
    file: UploadFile = File(...),
) -> Profile:  # noqa: D401
    """Create an extended facial profile with additional creative metrics."""
    content = await file.read()

    try:
        data = analyze_face(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Creative placeholder metrics (can be replaced with real models later)
    symmetry = round(1 - abs(data["eye_distance"] - 60) / 100, 2)
    emotion = "neutral"
    attractiveness = round((data["eye_distance"] / 100) * 5, 1)

    description = (
        f"Emotion: {emotion}; Symmetry: {symmetry}; "
        f"Attractiveness: {attractiveness}/5"
    )

    return Profile(
        landmarks=data["landmarks"],
        eye_distance=data["eye_distance"],
        yaw=data["yaw"],
        description=description,
        aligned_face=data.get("aligned_face"),
    )

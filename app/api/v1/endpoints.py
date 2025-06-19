from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.profile import Profile
from app.utils.face_analyzer import analyze_face

router = APIRouter()


@router.get("/ping", summary="Ping")
async def ping():
    """Simple liveness check."""
    return {"ping": "pong"}


@router.post("/create-profile", response_model=Profile, summary="Create facial profile")
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
    )

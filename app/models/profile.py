from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class Profile(BaseModel):
    """Represents a facial profile description with numeric metrics."""

    landmarks: List[Tuple[int, int]]
    eye_distance: float
    yaw: float
    description: Optional[str] = None
    aligned_face: Optional[str] = Field(
        default=None,
        description="Base-64 encoded 150×150 aligned face crop (JPEG)",
    )
    jitter_faces: Optional[List[str]] = Field(
        default=None,
        description="Five base-64 encoded jittered crops for augmentation (only returned by /store-profile)",
    )
    id: Optional[str] = Field(default=None, description="Unique profile identifier")

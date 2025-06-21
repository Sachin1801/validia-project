from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class Profile(BaseModel):
    """Represents a facial profile description with numeric metrics."""

    landmarks: List[Tuple[int, int]]
    eye_distance: float
    yaw: float
    description: Optional[str] = None
    id: Optional[str] = Field(default=None, description="Unique profile identifier")

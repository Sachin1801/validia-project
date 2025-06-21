from pydantic import BaseModel


class DeepfakeResult(BaseModel):
    """Simple schema for deep-fake detection stub."""

    is_deepfake: bool
    confidence: float  # 0.0 – 1.0
    description: str

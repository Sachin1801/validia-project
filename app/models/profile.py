from pydantic import BaseModel


class Profile(BaseModel):
    """Represents a facial profile description."""

    description: str

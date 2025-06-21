import uuid
from typing import Dict

from app.models.profile import Profile


class _InMemoryProfileStore:
    """Very simple in-process storage of profiles by UUID."""

    def __init__(self):
        self._store: Dict[str, Profile] = {}

    def add(self, profile: Profile) -> str:
        _id = str(uuid.uuid4())
        profile.id = _id
        self._store[_id] = profile
        return _id

    def get(self, profile_id: str) -> Profile:
        if profile_id not in self._store:
            raise KeyError(f"Profile '{profile_id}' not found")
        return self._store[profile_id]


profile_store = _InMemoryProfileStore()

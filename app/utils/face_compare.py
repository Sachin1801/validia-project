import numpy as np
from app.models.profile import Profile


def compare_profiles(p1: Profile, p2: Profile) -> float:
    """Compute a naive similarity score between two profiles (0 identical, higher worse).

    We align landmarks lists and calculate mean Euclidean distance, normalized by eye-distance.
    Returns: float distance (smaller means more similar)."""
    if len(p1.landmarks) != 68 or len(p2.landmarks) != 68:
        raise ValueError("Profiles must have 68 landmarks each")

    arr1 = np.array(p1.landmarks, dtype=float)
    arr2 = np.array(p2.landmarks, dtype=float)

    raw_dist = np.linalg.norm(arr1 - arr2, axis=1).mean()
    norm_factor = (p1.eye_distance + p2.eye_distance) / 2.0 or 1.0
    return raw_dist / norm_factor

## Commit 2: Facial Analysis with OpenCV & dlib

**Branch**: `commit-2-face-analysis`

### Directory Structure Updates

```bash
tree validia-project/app

app/
├── utils/
│   ├── __init__.py
│   └── face_analyzer.py    # new
├── api/
│   └── v1/
│       └── endpoints.py    # updated
├── models/
│   └── profile.py          # updated
└── tests/
    └── test_face_analyzer.py  # new
```

### 1. `app/utils/face_analyzer.py`

```python
import cv2
import dlib
from typing import Dict

# Initialize dlib's face detector and shape predictor
_detector = dlib.get_frontal_face_detector()
_predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")


def analyze_face(image_bytes: bytes) -> Dict[str, any]:
    """
    Detects facial landmarks and computes a simple profile dictionary.
    Returns:
      {
        "landmarks": List[ (x, y) ] for 68 points,
        "eye_distance": float,
        "yaw": float (placeholder),
      }
    """
    # Decode image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    rects = _detector(gray, 1)
    if not rects:
        raise ValueError("No face detected")

    # Take first face
    rect = rects[0]
    shape = _predictor(gray, rect)
    landmarks = [(pt.x, pt.y) for pt in shape.parts()]

    # Example metric: distance between eye corners
    left_eye = landmarks[36]  # point 37
    right_eye = landmarks[45] # point 46
    eye_distance = ((left_eye[0]-right_eye[0])**2 + (left_eye[1]-right_eye[1])**2)**0.5

    return {
        "landmarks": landmarks,
        "eye_distance": eye_distance,
        "yaw": 0.0  # placeholder for head pose estimation
    }
```

### 2. Update `app/models/profile.py`

```diff
 class Profile(BaseModel):
-    description: str
+    landmarks: List[Tuple[int, int]]
+    eye_distance: float
+    yaw: float
+    description: Optional[str] = None  # human-readable summary
```

### 3. Update endpoint in `app/api/v1/endpoints.py`

```diff
 @router.post(
     "/create-profile",
-    response_model=Profile,
+    response_model=Profile,
 )
 async def create_profile(file: UploadFile = File(...)) -> Profile:
     content = await file.read()
-    # Placeholder
-    return Profile(description="Example facial profile based on analysis.")
+    try:
+        profile_data = analyze_face(content)
+    except ValueError as e:
+        raise HTTPException(status_code=400, detail=str(e))
+
+    # Build summary
+    summary = f"Detected face with eye distance {profile_data['eye_distance']:.1f}px"
+    return Profile(
+        landmarks=profile_data["landmarks"],
+        eye_distance=profile_data["eye_distance"],
+        yaw=profile_data["yaw"],
+        description=summary
+    )
```

Be sure to import:

```python
from app.utils.face_analyzer import analyze_face
from typing import List, Tuple, Optional
import numpy as np
```

### 4. Tests in `app/tests/test_face_analyzer.py`

```python
import pytest
from app.utils.face_analyzer import analyze_face

@ pytest.fixture
def sample_image_bytes():
    with open("tests/data/sample_face.jpg", "rb") as f:
        return f.read()

def test_analyze_face_success(sample_image_bytes):
    result = analyze_face(sample_image_bytes)
    assert "landmarks" in result and len(result["landmarks"]) == 68
    assert result["eye_distance"] > 0

def test_analyze_face_no_face():
    with pytest.raises(ValueError):
        analyze_face(b"not an image")
```

### 5. Docs: `docs/face_analysis.md`

```markdown
# Commit 2: Facial Analysis

This document covers:

1. **Purpose**: Integrate dlib for landmark detection, compute key metrics.
2. **Usage**: `/api/v1/create-profile` now returns detailed profile JSON.
3. **Head Pose**: Placeholder for yaw; future work will add full pose estimation.
4. **Testing**: Unit tests validate both success and failure modes.
```

### 6. Notebook: `notebooks/commit2_face_analysis.ipynb`

- Demonstrate calling `analyze_face` on sample images.
- Visualize landmarks overlaid on images.
- Test endpoint via `requests` library.

---

**Prompt for Cursor (o3) model**:

```
# Start branch commit-2-face-analysis
# Update docs/face_analysis.md: Add usage example and troubleshooting tips for missing model file
```


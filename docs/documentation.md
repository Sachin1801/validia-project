# Validia – Complete Documentation

This file consolidates the following individual documents into one place:

* `project_overview.md`
* `api_reference.md`
* `initial_setup.md`
* `bonus_features.md`
* `face_analysis.md`

---

## 1. Project Overview

<!-- BEGIN: project_overview.md -->
# Validia Project – Consolidated Documentation (Commit 4)

> This document supersedes the earlier `face_analysis.md`, `bonus_features.md`, and `initial_setup.md`. It walks a newcomer through installing the project, understanding its architecture, and exercising every API endpoint in chronological order.

---

## 1. Project Purpose

Validia is a FastAPI-based service that offers:

1. Facial landmark extraction (dlib + OpenCV).
2. Basic and creative facial-profile generation.
3. Stub bonus endpoints for liveness & deep-fake checks.
4. A simple identification flow (store → compare) to demonstrate how profiles could be matched.

---

## 2. Quick‐start Checklist (macOS / Linux / Windows)

### 2.1 Python & Virtual-env

| Component | Required version |
|-----------|------------------|
| Python    | **3.11** (matches wheels in `requirements.txt`) |
| dlib      | **19.24.4**      |

Why these exact versions?

* The PyPI wheel for `dlib==19.24.4` is available for CPython 3.11 on all desktop OSes. The more recent `20.0.0` (released May 27, 2025) is supported in this project as it does not yet ship universal wheels and will attempt a painful source build.
* OpenCV, FastAPI and NumPy versions in `requirements.txt` have been tested against 3.11.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt      # pulls dlib==19.24.4 wheel – no compile step
```

If `pip` attempts to **build** dlib:

1. Verify you are really using Python 3.11 **64-bit**.
2. Install CMake ≥3.22 and, on Windows, the *Visual Studio 2022 C++ Build Tools*.

```bash
# Windows one-liners (PowerShell)
winget install kitware.cmake --source winget
winget install Microsoft.VisualStudio.2022.BuildTools --source winget
```

---

### 2.2 Download the Landmark Model (≈100 MB)

```bash
mkdir -p models
curl -L -o models/shape_predictor_68_face_landmarks.dat.bz2 \
     https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -dk models/shape_predictor_68_face_landmarks.dat.bz2   # leaves the .dat file
```

---

## 3. Running the API

```bash
uvicorn app.main:app --reload
open http://localhost:8000/docs   # interactive Swagger UI
```

Tag overview inside Swagger:

* **facial-profile** – `/create-profile` and `/create-profile-extended`
* **bonus**          – liveness & deep-fake stubs + profile store/identify

---

## 4. Chronological Feature Walkthrough

### 4.1 Health Check (Commit 1)
```bash
curl http://localhost:8000/v1/ping     # → {"ping":"pong"}
```

### 4.2 Basic Profile (Commit 2)
```bash
curl -F "file=@face.jpg" http://localhost:8000/v1/create-profile
```
Returns 68 landmarks, eye-distance, yaw, description.

### 4.3 Verify Face – Liveness Stub (Commit 3)
```bash
curl -F "file=@face.jpg" http://localhost:8000/v1/verify-face
```
Same JSON plus a liveness note.

### 4.4 Deep-fake Detection Stub (Commit 3)
```bash
curl -F "file=@frame.jpg" http://localhost:8000/v1/detect-deepfake
```
Random-but-deterministic `confidence` and `is_deepfake` keys.

### 4.5 Creative Profile (Commit 4)
```bash
curl -F "file=@face.jpg" http://localhost:8000/v1/create-profile-extended
```
Adds placeholder `emotion`, `symmetry`, and `attractiveness`.

### 4.6 Identification Flow (Task 4)
```bash
# 1) store a reference face
a=$(curl -s -F "file=@me1.jpg" http://localhost:8000/v1/store-profile | jq -r .id)

# 2) compare another photo of you
curl -F "file=@me2.jpg" "http://localhost:8000/v1/identify-face?profile_id=$a"
```
Response contains `is_match`, `distance`, and threshold.

---

## 5. Error Codes

| Code | When it happens |
|------|-----------------|
| 400  | Invalid image bytes or no face detected |
| 404  | Unknown `profile_id` in `/identify-face` |
| 422  | Missing file field in multipart upload |
| 500  | Landmark model not found / cannot load |

---

## 6. Development Commands

```bash
pytest -q                # 7 tests – all must pass
ruff check               # style/lint (if ruff installed)
uvicorn app.main:app --reload
```

---

## 7. Next Steps

1. Replace stub confidence & creative metrics with real ML models.
2. Persist profiles in a database (SQLite or PostgreSQL) instead of RAM.
3. Add JWT-based authentication and rate-limiting.

---

## 8. New Enhancements (Commit 5)

The following improvements have been merged after Commit 4 and are already live in the API:

1. **Quality Gate** – images are rejected with HTTP 400 if brightness is outside 60–200 or Laplacian variance is <100 (too dark/blurry).
2. **Aligned Face Chip** – every profile now carries a base-64 encoded 150 × 150 crop (`aligned_face`).  Helpful for quick previews and later embedding extraction.
3. **Jittered Augmentation** – `/store-profile` saves five augmented face crops (`jitter_faces`) along with the reference profile to improve robustness of matching.

These changes require no additional setup. The wheel for `dlib` ≥19.24.4 already provides `get_face_chip()` and `jitter_image()`. Ensure the landmark `.dat` file is present as described in section 2.2.
<!-- END: project_overview.md -->

---

## 2. API Reference

<!-- BEGIN: api_reference.md -->
# API Reference (Commit 4)

This document outlines usage examples for all public API endpoints exposed by the Validia face analysis service.

---

## Base URL

```text
http://localhost:8000
```

All endpoints below are prefixed with `/api/v1` when the server is started with the default configuration.

---

## 1. Health Checks

### 1.1 `GET /api/v1/ping`

Curl:
```bash
curl -X GET "http://localhost:8000/api/v1/ping"
```

Python:
```python
import requests
requests.get("http://localhost:8000/api/v1/ping").json()
```

---

## 2. Face Profiling

### 2.1 `POST /api/v1/create-profile`

Upload an image to generate basic facial landmarks and metrics.

Curl:
```bash
curl -X POST "http://localhost:8000/api/v1/create-profile" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@face.jpg"
```

Python:
```python
import requests
with open("face.jpg", "rb") as f:
    res = requests.post(
        "http://localhost:8000/api/v1/create-profile",
        files={"file": ("face.jpg", f, "image/jpeg")},
    )
print(res.json())
```

---

### 2.2 `POST /api/v1/create-profile-extended`

Generates additional creative attributes such as emotion, symmetry, and an attractiveness score.

Curl:
```bash
curl -X POST "http://localhost:8000/api/v1/create-profile-extended" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@face.jpg"
```

---

## 3. Bonus Endpoints

See `docs/bonus_features.md` for Verify-Face and Deepfake detection usage.

---

## 4. OpenAPI / Swagger UI

Navigate to:

```text
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/redoc      # ReDoc UI
http://localhost:8000/openapi.json
```
<!-- END: api_reference.md -->

---

## 3. Initial Setup

<!-- BEGIN: initial_setup.md -->
# Initial Setup

This document captures the initial directory structure and setup commands for the Validia project.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# If pip falls back to building dlib from source install:
#   * "Visual Studio 2022 C++ Build Tools"
#   * CMake 3.22+

uvicorn app.main:app --reload
```

## Download landmark model

```bash
curl -L -o models/shape_predictor_68_face_landmarks.dat.bz2 \
     https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -dk models/shape_predictor_68_face_landmarks.dat.bz2
```
<!-- END: initial_setup.md -->

---

## 4. Bonus Features

<!-- BEGIN: bonus_features.md -->
# Bonus Features

This document summarises the experimental endpoints that extend the core face-profiling service.

For full request/response examples see the dedicated sections in **[API Reference](api_reference.md#3-bonus-endpoints)**.

---

## Endpoints

| Path | Summary |
|------|---------|
| `POST /api/v1/verify-face` | Generate a profile and perform a stub liveness check |
| `POST /api/v1/detect-deepfake` | Return a confidence score indicating whether the image is likely a deepfake |

---

### Verify Face

The endpoint returns the same `Profile` schema used by `/create-profile` but with an additional description indicating liveness.

### Detect Deepfake

Returns a JSON object with two keys:

```json
{
  "is_deepfake": false,
  "confidence": 0.42,
  "description": "Likely genuine"
}
```

Confidence is a deterministic pseudo-random value for now and will be replaced by a real detector model in future iterations.
<!-- END: bonus_features.md -->

---

## 5. Facial Analysis

<!-- BEGIN: face_analysis.md -->
# Facial Analysis (Commit 2)

This document describes the second milestone which introduces facial landmark detection using **dlib** and **OpenCV**.

## New Components

1. `app/utils/face_analyzer.py` – wraps face detection & landmark inference.
2. `app/models/profile.py` – expanded to include numeric metrics.
3. `/api/v1/create-profile` – new endpoint returning a `Profile` JSON.
4. `app/tests/test_face_analyzer.py` – unit tests covering edge-cases.

### Bonus Features (Commit 3)

5. `app/api/v1/bonus_endpoints.py` – extra endpoints under the "bonus" tag:
   * `POST /v1/verify-face` – same as `create-profile` but embellished with a liveness-check placeholder.
   * `POST /v1/detect-deepfake` – returns a *stub* deep-fake confidence value.

### Identification (Task 4)

6. `app/utils/profile_store.py` – in-memory storage of generated profiles.
7. `app/utils/face_compare.py` – very naive similarity metric.
8. Additional endpoints:
   * `POST /v1/store-profile` → saves a profile and returns its `id`.
   * `POST /v1/identify-face?profile_id=...` → compares another image with that reference and answers `{is_match, distance, threshold}`.

## Prerequisites

This feature relies on the dlib landmark predictor model:

```
wget https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat -P models/
```

## Usage

Run the API locally:
```bash
uvicorn app.main:app --reload
```

Upload an image via Swagger UI (`/docs`) or cURL:
```bash
curl -X POST -F "file=@face.jpg" http://127.0.0.1:8000/v1/create-profile
```

Example response:
```json
{
  "landmarks": [[34, 60], [35, 65], ...],
  "eye_distance": 123.4,
  "yaw": 0.0,
  "description": "Detected face with eye distance 123.4px and yaw 0.0."
}
```

### Identifying a face

```bash
# 1. Store a reference profile and capture its id
REF_ID=$(curl -s -F "file=@face1.jpg" http://127.0.0.1:8000/v1/store-profile | jq -r .id)

# 2. Compare another image against that profile
curl -F "file=@face2.jpg" "http://127.0.0.1:8000/v1/identify-face?profile_id=$REF_ID"
```

### Deep-fake stub

```bash
curl -F "file=@video_frame.jpg" http://127.0.0.1:8000/v1/detect-deepfake
```

Example `create-profile` response:

## Troubleshooting

* **Missing model file** – You will receive a `500` error with a message guiding you to download the `.dat` file.
* **No face detected** – The endpoint returns `400` with an explanatory message.
<!-- END: face_analysis.md -->

---

*End of consolidated documentation.* 
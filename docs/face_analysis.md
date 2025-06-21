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
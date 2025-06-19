# Facial Analysis (Commit 2)

This document describes the second milestone which introduces facial landmark detection using **dlib** and **OpenCV**.

## New Components

1. `app/utils/face_analyzer.py` – wraps face detection & landmark inference.
2. `app/models/profile.py` – expanded to include numeric metrics.
3. `/api/v1/create-profile` – new endpoint returning a `Profile` JSON.
4. `app/tests/test_face_analyzer.py` – unit tests covering edge-cases.

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

## Troubleshooting

* **Missing model file** – You will receive a `500` error with a message guiding you to download the `.dat` file.
* **No face detected** – The endpoint returns `400` with an explanatory message. 
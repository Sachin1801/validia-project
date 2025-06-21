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
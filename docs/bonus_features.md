# Bonus Features

This document lists **experimental** or **extended** endpoints that go beyond the minimal "create-profile" flow described in the main docs.  They showcase ideas such as liveness checks, deep-fake stubs, in-memory identification, and the newest image-quality & augmentation helpers.

---

## 1. Endpoint Matrix

| Path | Tag | Purpose | Extras returned |
|------|-----|---------|-----------------|
| `POST /api/v1/verify-face` | bonus | Generate a profile **plus** a stub liveness description | `aligned_face` (base-64) |
| `POST /api/v1/detect-deepfake` | bonus | Return a deterministic pseudo-confidence for deep-fake detection | – |
| `POST /api/v1/store-profile` | bonus | Create & store a reference profile in RAM | `id`, `aligned_face`, `jitter_faces[]` |
| `POST /api/v1/identify-face?profile_id={id}` | bonus | Compare a probe image against a stored reference and answer if it's the same person | `is_match`, `distance`, `threshold` |

All routes share the same **multipart/form-data** image upload style used elsewhere in the API.

---

## 2. New Fields Introduced by Enhancements

| Field | Type | Added in | Meaning |
|-------|------|----------|---------|
| `aligned_face` | Base-64 string (JPEG) | Commit 5 | 150 × 150 upright crop generated with `dlib.get_face_chip()` so you can preview or embed it easily. |
| `jitter_faces` | List[str] | Commit 5 | Five random jittered crops (data augmentation) returned by `/store-profile` for robustness testing. |

The original `Profile` fields (`landmarks`, `eye_distance`, `yaw`, `description`) remain unchanged.

---

## 3. Quality Gate – Why Your Upload Might Fail

Before any detection starts we now run two quick heuristics:

* **Brightness** must be between **60 – 200** (0–255 scale).  Too dark/bright → `400` with message "Image brightness X outside acceptable range".
* **Sharpness** measured via **variance of Laplacian** must be **≥ 100**.  Blurry images are rejected with `400`.

These checks help users correct obvious mistakes early and keep later metrics meaningful.

---

## 4. Verify Face

```bash
curl -F "file=@selfie.jpg" http://localhost:8000/api/v1/verify-face | jq .
```

Example response (truncated):

```jsonc
{
  "landmarks": [[123, 321], … ],
  "eye_distance": 61.4,
  "yaw": 0.1,
  "aligned_face": "<base-64 JPEG>",
  "description": "Face OK. Eye distance: 61.4px and yaw 0.1. (Liveness check: stub, always passes)"
}
```

---

## 5. Deep-fake Stub

`/detect-deepfake` still returns a deterministic pseudo-random number (`confidence`) so examples stay reproducible.  It will be swapped for a true CNN in a later milestone.

---

## 6. Identification Walk-through

```bash
# 1) store a reference face
a=$(curl -s -F "file=@me1.jpg" http://localhost:8000/api/v1/store-profile | jq -r .id)

# 2) compare another image of you
curl -F "file=@me2.jpg" "http://localhost:8000/api/v1/identify-face?profile_id=$a" | jq .
```
Returns e.g.

```json
{
  "is_match": true,
  "distance": 0.07,
  "threshold": 0.1,
  "reference_id": "01234567-89ab-cdef-0123-456789abcdef"
}
```

Internally we compute a naive landmark distance; a real embedding model is on the roadmap.

---

## 7. Roadmap – What's Next?

1. **CNN face-detector** (`dlib.cnn_face_detection_model_v1`) for better recall & speed.
2. **128-D embeddings** (`dlib.face_recognition_model_v1`) to replace the landmark-distance comparator.
3. **Blink / mouth-ratio liveness** using existing landmarks.
4. Persist profiles in **SQLite/Redis** instead of RAM.
5. Optional **JWT auth & rate-limit** for production setups.

*Have an idea or want to contribute?* Open an issue or PR in the repository. 
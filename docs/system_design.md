# Validia – System Design Overview

```mermaid
flowchart TD
    subgraph Client
        A["Browser / Mobile App<br/>(curl, Swagger UI, JS)"]
    end

    subgraph API[FastAPI Service]
        B[main.py] -->|include_router| C[api/v1/endpoints.py]
        B --> D[api/v1/bonus_endpoints.py]
    end

    subgraph Utils
        C1[face_analyzer.py] -->|dlib + OpenCV| E((dlib C++))
        C2[profile_store.py]((RAM))
        C3[face_compare.py]
    end

    subgraph Enhancements
        U1[quality_gate (brightness + sharpness)]
        U2[alignment helper (get_face_chip)]
        U3[data_augment (jitter_image)]
    end

    C1 --> U1
    U1 --> U2 --> U3

    subgraph Models
        F[profile.py]
        G[deepfake.py]
    end

    A -->|HTTP multipart-image| C
    A --> D

    C -->|create-profile| C1 --> F
    D -->|verify-face| C1
    D -->|deepfake| G
    D -->|store-profile| C1 --> C2
    D -->|identify-face| C2 --> C3

    E -. loads .-> H[shape_predictor_68_face_landmarks.dat]
```

### Flow Description

1. **Client** uploads an image (multipart/form-data) to one of the REST endpoints.
2. `endpoints.py` / `bonus_endpoints.py` read the bytes and pass them to `face_analyzer.py`.
3. `face_analyzer.py` decodes the image with OpenCV, loads the pretrained dlib landmark model from disk (≈100 MB), and returns 68 landmarks + basic metrics.
4. Depending on the route:
   * The data is returned directly (`create-profile`, `verify-face`).
   * Saved into the in-memory `profile_store.py` (`store-profile`).
   * Compared against a stored reference via `face_compare.py` (`identify-face`).
   * Passed through a stub heuristic to simulate deep-fake detection (`detect-deepfake`).
5. JSON responses are serialized by Pydantic models and sent back to the client.

### Deployment Notes

* **Stateless** – Identification storage is in-memory; restart loses profiles (swap with a DB for prod).
* **CPU-only** – Dlib's HOG detector runs on CPU; OpenCV is the headless wheel.
* **Single binary dependency** – Only the .dat landmark model is required at runtime (no other external assets).

### Scaling Ideas

* Add Redis or PostgreSQL for persistent profile storage.
* Off-load compute-heavy detection models to GPU micro-service.
* Place Uvicorn behind an ASGI server like `uvicorn --workers 4` or `gunicorn -k uvicorn.workers.UvicornWorker`. 
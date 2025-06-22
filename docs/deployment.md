# Deployment Guide

This page explains how to run Validia locally via Docker and how the CI pipeline works.

---

## 1. Build & Run with Docker

```bash
# first build (installs build-essential + CMake, compiles dlib 20.0.0)
docker build -t validia .

# Run on http://localhost:8000
docker run -p 8000:80 validia

http://127.0.0.1:8000/docs this is where you can test and view all the endpoints created
```

### Live-reload during development

Use **docker-compose** which mounts the project folder as a volume:

```bash
docker compose up --build  # ctrl-c to stop
```

Any code change triggers Uvicorn reload inside the container.

---

## 2. GitHub Actions CI

The workflow file at `.github/workflows/ci.yml` runs on every push / PR against `main`:

1. Checkout code
2. Install Python 3.11 and project dependencies
3. Run `pytest` (unit tests)
4. Lint with **ruff**

A green badge will appear in PRs if both steps pass.

---

## 3. Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_PREFIX` | `/api/v1` | Exposed in Docker Compose for flexibility |

---

## 4. Production Tips

* Use a more robust ASGI server like **gunicorn**: `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`.
* Mount the `models/shape_predictor_68_face_landmarks.dat` into the container at build time.
* Add `--workers 4` for multi-core deployments.

Refer to `docs/system_design.md` for scaling ideas. 
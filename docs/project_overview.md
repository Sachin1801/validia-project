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
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
| dlib      | **20.0.0**      |

Why these exact versions?

* The PyPI wheel for `dlib==20.0.0` (released May 27, 2025) is now available and fully supported in this project. It ships with universal wheels that make installation much easier across all platforms.
* OpenCV, FastAPI and NumPy versions in `requirements.txt` have been tested against 3.11.
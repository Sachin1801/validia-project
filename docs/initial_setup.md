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
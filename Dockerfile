FROM python:3.11-slim

# System-wide build deps for dlib when wheel not available
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
      libopenblas-dev \
      liblapack-dev \
      pkg-config \
      wget \
      && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
      PYTHONUNBUFFERED=1

WORKDIR /app

# Upgrade pip first to ensure latest wheel resolution
RUN python -m pip install --upgrade pip

# Install python deps (minus dlib)
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

# Install specific dlib version (20.0.0) separately so build logs are clearer
RUN pip install --no-cache-dir dlib==20.0.0

# Copy source last to leverage Docker cache
COPY . .

# Download landmark model at build time (≈100 MB) – keep layer cachable
RUN mkdir -p models && \
      wget -qO- \
      https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2 \
      | bunzip2 -c > models/shape_predictor_68_face_landmarks.dat

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"] 
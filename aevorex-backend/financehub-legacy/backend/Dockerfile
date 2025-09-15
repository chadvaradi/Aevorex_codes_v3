# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tooling
RUN pip install --upgrade pip

# Copy backend requirements from repo root context
COPY modules/financehub/backend/requirements.txt ./requirements.txt

# Build wheels for faster final install
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final runtime image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps from wheels
COPY --from=builder /app/wheels /wheels/
COPY modules/financehub/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ -r requirements.txt

# Copy full modules tree so imports like `modules.financehub.backend.*` work
COPY modules /app/modules

# Cloud Run expects the container to listen on $PORT (default 8080)
EXPOSE 8080

CMD ["sh", "-c", "uvicorn modules.financehub.backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

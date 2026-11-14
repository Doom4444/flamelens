# Production image for the FlameLens FastAPI backend.
#
# Build from the repository root so the four NASA PSI metadata inventories can
# be copied into the image:
#
#   docker build -t flamelens-api .
#   docker run -p 8000:8000 -e CORS_ORIGINS=http://localhost:5173 flamelens-api

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create an unprivileged runtime user.
RUN groupadd --system flamelens \
    && useradd --system --gid flamelens --create-home flamelens

WORKDIR /app

COPY backend/requirements-prod.txt /app/requirements-prod.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements-prod.txt

# Application source (no tests, tooling or local virtualenv).
COPY backend/app /app/app

# Ship the Stage 1 NASA PSI inventories inside the image. These are the only
# runtime data files the API needs; nothing else from data/ is copied.
COPY data/metadata/investigations_inventory.json \
     data/metadata/datasets_inventory.json \
     data/metadata/files_inventory.json \
     data/metadata/storage_summary.json \
     /app/data/metadata/

ENV ENVIRONMENT=production \
    DEBUG=false \
    HOST=0.0.0.0 \
    PORT=8000 \
    FLAMELENS_METADATA_DIR=/app/data/metadata

RUN chown -R flamelens:flamelens /app
USER flamelens

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/api/v1/health', timeout=3)"

# Honour the port assigned by the hosting provider (Render sets PORT).
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]

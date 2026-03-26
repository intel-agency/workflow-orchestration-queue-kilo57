# OS-APOW Dockerfile
# Multi-stage build for production deployment

FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Development stage
FROM base AS development

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Default command for development
CMD ["uvicorn", "src.notifier_service:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install production dependencies only
RUN uv pip install --system .

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command for production
CMD ["uvicorn", "src.notifier_service:app", "--host", "0.0.0.0", "--port", "8000"]

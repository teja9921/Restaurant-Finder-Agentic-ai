# Multi-stage build for smaller image
FROM python:3.11.5-slim AS builder

WORKDIR /app

# Install uv for fater dependency resolution
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

#Install dependencies to /app/.venv
RUN uv sync --no-dev

#Final stage
FROM python:3.11.5-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/ping')" || exit 1

# Run application
CMD ["python", "-m", "src.api"]

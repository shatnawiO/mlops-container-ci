# ============================================================================
# STAGE 1: Build & Dependency Stage
# Multi-stage build separates compiler/packaging bloat from production runtime.
# Base image is pinned to an immutable SHA256 digest for 100% reproducible builds.
# ============================================================================
FROM python:3.11.9-slim@sha256:8fb099199b9f2d70342674bd9dbccd3ed03a258f26bbd1d556822c6dfc60c317 AS builder

# Prevent python from writing bytecode and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Create isolated virtual environment for clean copy to final stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies without caching wheel archives to minimize layer size
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ============================================================================
# STAGE 2: Production Runtime Stage
# Minimal, attack-surface reduced image running as an unprivileged non-root user.
# ============================================================================
FROM python:3.11.9-slim@sha256:8fb099199b9f2d70342674bd9dbccd3ed03a258f26bbd1d556822c6dfc60c317 AS runtime

# Python runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Create dedicated non-root system user and group (UID/GID 1000)
# Running as non-root prevents container breakout / host privilege escalation
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy the pre-built virtualenv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source code and model artifacts into the container
COPY src /app/src
COPY models /app/models

# Adjust ownership to unprivileged user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the API port
EXPOSE 8000

# Native healthcheck using python's built-in urllib (avoids installing curl, reducing CVE attack surface)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start FastAPI application using uvicorn
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

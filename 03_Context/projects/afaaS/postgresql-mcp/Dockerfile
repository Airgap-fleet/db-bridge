# Multi-stage Dockerfile for DB Bridge
# ==============================================================================
# Stage 1: Builder - Install dependencies and build package
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install dependencies and build package
RUN uv pip install --system --no-cache-dir -e .

# ==============================================================================
# Stage 2: Runtime - Minimal runtime image
# ==============================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r mcp && useradd -r -g mcp -u 10001 -s /sbin/nologin mcp

# Copy installed package from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/db-bridge /usr/local/bin/db-bridge

# Create non-root user and set ownership
RUN chown -R mcp:mcp /app

USER mcp

# Environment variables
ENV DB_BRIDGE_TRANSPORT=stdio \
    DB_BRIDGE_LOG_LEVEL=INFO \
    DB_BRIDGE_POOL_MIN_SIZE=1 \
    DB_BRIDGE_POOL_MAX_SIZE=10 \
    DB_BRIDGE_QUERY_TIMEOUT=30 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import postgresql_mcp; print('healthy')" || exit 1

# Expose ports for SSE/HTTP transports
EXPOSE 8000

# Entry point
ENTRYPOINT ["db-bridge"]
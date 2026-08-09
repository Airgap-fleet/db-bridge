# Multi-stage Dockerfile for Filesystem MCP Server
# Uses python:3.12-slim for minimal size

# ==============================================================================
# Stage 1: Builder - Install dependencies and build package
# ==============================================================================
FROM python:3.12-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install hatch
RUN pip install --no-cache-dir hatch

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Build the package
RUN hatch build && pip install --no-cache-dir dist/*.whl

# ==============================================================================
# Stage 2: Runtime - Minimal runtime image
# ==============================================================================
FROM python:3.12-slim AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Set working directory
WORKDIR /app

# Copy installed package from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/filesystem-mcp /usr/local/bin/filesystem-mcp

# Create sandbox directory (will be mounted at runtime)
RUN mkdir -p /sandbox && chown appuser:appuser /sandbox

# Switch to non-root user
USER appuser

# Environment variables
ENV FILESYSTEM_MCP_ROOT_PATH=/sandbox
ENV FILESYSTEM_MCP_MAX_FILE_SIZE=10485760
ENV FILESYSTEM_MCP_FOLLOW_SYMLINKS=false
ENV FILESYSTEM_MCP_ALLOW_ABSOLUTE_PATHS=false
ENV FILESYSTEM_MCP_DEFAULT_ENCODING=utf-8

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import filesystem_mcp; print('healthy')" || exit 1

# Entry point
ENTRYPOINT ["filesystem-mcp"]
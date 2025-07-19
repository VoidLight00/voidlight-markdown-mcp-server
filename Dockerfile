# VoidLight MarkItDown MCP Server Docker Image
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md LICENSE ./

# Install build dependencies and build wheel
RUN python -m pip install --upgrade pip hatchling
RUN python -m pip wheel --no-deps --wheel-dir wheels .

# Runtime stage
FROM python:3.11-slim as runtime

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 mcp

# Set working directory
WORKDIR /app

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libmagic1 \
    tesseract-ocr \
    tesseract-ocr-kor \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /build/wheels/*.whl ./

# Install the application with core dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install *.whl && \
    rm -f *.whl

# Create directories for data processing
RUN mkdir -p /workdir /app/temp && \
    chown -R mcp:mcp /workdir /app

# Switch to non-root user
USER mcp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_WORKDIR=/workdir

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import voidlight_markitdown_mcp; print('OK')"

# Expose port (for future HTTP API)
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["voidlight-markitdown-mcp"]

# Default command is to run the MCP server
CMD []
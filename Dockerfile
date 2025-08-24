# Jarvis AI - Docker Container for Consistent Environments
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY pyproject.toml /tmp/

# Install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements_enhanced.txt

# Production stage  
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    JARVIS_DATA_DIRECTORY="/app/data" \
    JARVIS_LOGS_DIRECTORY="/app/logs" \
    JARVIS_PLUGINS_DIRECTORY="/app/plugins"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r jarvis && useradd -r -g jarvis jarvis

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p data logs config plugins checkpoints && \
    chown -R jarvis:jarvis /app

# Copy application code
COPY --chown=jarvis:jarvis . .

# Install Jarvis AI package
RUN pip install -e .

# Copy default configuration

# Create healthcheck script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8501/_stcore/health || exit 1' > /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# Switch to non-root user
USER jarvis

# Expose port
EXPOSE 8501

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["/usr/local/bin/healthcheck.sh"]

# Default command
CMD ["jarvis", "run", "--host", "0.0.0.0", "--port", "8501"]

# Labels for metadata
LABEL org.opencontainers.image.title="Jarvis AI"
LABEL org.opencontainers.image.description="Privacy-first modular AI development assistant"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.authors="Jimmy De Jesus"
LABEL org.opencontainers.image.source="https://github.com/jimmyjdejesus-cmyk/Jarvis_AI"
LABEL org.opencontainers.image.documentation="https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/docs"
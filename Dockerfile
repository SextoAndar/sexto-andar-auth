# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy scripts
COPY scripts/ ./scripts/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8001

# Health check - normalize API_BASE_PATH then hit the correct /health path
# If API_BASE_PATH is empty or "/" the path becomes "/health", otherwise
# we append "/health" to the trimmed base path (avoids `//health` 404s).
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD sh -c 'p=${API_BASE_PATH:-/}; p=${p%/}; if [ -z "${p}" ] || [ "${p}" = "/" ]; then path="/health"; else path="${p}/health"; fi; curl -fsS -o /dev/null "http://localhost:8001${path}" || exit 1'

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

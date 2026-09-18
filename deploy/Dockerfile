# ==============================================================================
# 🚀 TGFORWARDER - ENTERPRISE PRODUCTION DOCKER ENGINE
# ==============================================================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install native compilation dependencies for cryptg & uvloop acceleration
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY . .

# Create volume mount points for persistent session, DB, and logs
VOLUME ["/app/logs", "/app/db_backups"]

# Default entrypoint runs the main forwarder
CMD ["python", "main.py"]

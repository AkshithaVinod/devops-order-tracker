# Stage 1: Build stage (prepare everything)
FROM python:3.11-slim as builder

WORKDIR /build

# Install system tools we need to compile Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Runtime stage (the actual app)
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user (safer, not running as admin)
RUN useradd -m -u 1000 appuser

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder (stage 1)
COPY --from=builder /root/.local /home/appuser/.local

# Copy your app code
COPY --chown=appuser:appuser app/ app/
COPY --chown=appuser:appuser tests/ tests/
COPY --chown=appuser:appuser requirements.txt .

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.main

# Switch to non-root user (security)
USER appuser

# Health check (Docker will check if app is alive)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Expose port 5000 (tells Docker: this app uses port 5000)
EXPOSE 5000

# Run the app
CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "5000"]
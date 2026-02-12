FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY docstring_agent/ ./docstring_agent/
COPY cli.py .
COPY setup.py .
COPY pyproject.toml .

# Install package in development mode
RUN pip install -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for API server
EXPOSE 8000

# Default command shows help
CMD ["python", "-m", "app", "--help"]

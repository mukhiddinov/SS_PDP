# Base image
FROM python:3.11-slim

# Workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install system deps + Python deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run combined bot + API
CMD ["python", "main_combined.py"]

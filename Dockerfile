# Base image
FROM python:3.11-slim

# Workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install system deps (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && pip install --no-cache-dir -r /app/requirements.txt 
# Copy project
COPY . /app

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run both bot + API inside one process manager
# We will use "sh -c" to run two services at once
CMD ["sh", "-c", "\
    python nmadur_bot/main.py & \
    uvicorn nmadur_api.nmadur_api:app --host 0.0.0.0 --port 10000 \
"]

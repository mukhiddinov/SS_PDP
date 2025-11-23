# Hozirgi Dockerfile boshida o'zgarishlar kerak emas
FROM python:3.11-slim

WORKDIR /app

# requirements
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=10000  # Render tomonidan o'rnatiladigan $PORT ga ham mos

# CMD hozirgi main.py orniga start_server.py
CMD ["python", "nmadur_bot/start_server.py"]

FROM python:3.11-slim

WORKDIR /app

# requirements
COPY nmadur_bot/requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY nmadur_bot /app

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]

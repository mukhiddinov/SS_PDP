FROM python:3.11-slim

WORKDIR /app

# requirements
COPY nmadur_api/requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY nmadur_api /app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "nmadur_api:app", "--host", "0.0.0.0", "--port", "8000"]

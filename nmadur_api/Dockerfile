# Python 3.11 slim
FROM python:3.11-slim

# Ishchi papka
WORKDIR /app

# System dependencies va Python packages
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Hammasini papkaga ko‘chirish
COPY . /app

# Loglar darhol chiqishi uchun
ENV PYTHONUNBUFFERED=1

# API ishga tushirish komandasi
CMD ["uvicorn", "nmadur_api:app", "--host", "0.0.0.0", "--port", "8000"]

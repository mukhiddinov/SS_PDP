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
# Render Web service uchun portni olish shart
ENV PORT=10000

# Botni ishga tushiramiz
CMD ["python", "main.py"]

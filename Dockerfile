# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

# App
COPY . .

# Expose
EXPOSE 8080

# Env for Flask
ENV OAUTHLIB_INSECURE_TRANSPORT=1 \
    PYTHONIOENCODING=utf-8 \
    FLASK_ENV=production

# Start with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "premium_auto_blogger_web:app", "--workers", "2", "--threads", "4", "--timeout", "120"]



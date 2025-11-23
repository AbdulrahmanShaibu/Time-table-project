# Dockerfile for Flask app
FROM python:3.11-slim

# set a simple working dir
WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first for caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

# create non-root user
RUN useradd -ms /bin/bash appuser && chown -R appuser /app
USER appuser

ENV FLASK_APP=run.py

EXPOSE 5000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "4"]

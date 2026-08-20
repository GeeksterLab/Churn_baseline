FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api ./api
COPY core ./core
COPY models ./models

CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT}"]

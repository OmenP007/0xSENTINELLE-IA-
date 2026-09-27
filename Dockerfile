# Dockerfile multi-stage pour 0xSentinelle IA
FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système requises pour audio/RAG
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt python-telegram-bot

# Copie du code source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

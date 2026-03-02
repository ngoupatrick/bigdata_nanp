FROM python:3.11-slim

# Évite la création de fichiers .pyc et active l'affichage en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances sans cache
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "main.py"]
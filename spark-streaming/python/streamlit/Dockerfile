FROM python:3.11-slim

# Évite la création de fichiers .pyc et active l'affichage en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système pour mysql-connector
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances sans cache
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
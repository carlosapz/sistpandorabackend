# Imagen base
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crea la carpeta de la app
WORKDIR /app

# Copia requirements e instala Python deps
COPY requirements.txt /app/

# Actualiza pip e instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flower


# Copiar todo el proyecto
COPY . /app/

# Comando por defecto (lo puedes sobrescribir en docker-compose)
CMD ["gunicorn", "constructora.wsgi:application", "--bind", "0.0.0.0:8000"]

# Puerto expuesto
EXPOSE 8000

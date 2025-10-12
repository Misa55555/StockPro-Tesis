# ----
# Etapa 1: La Base
# ----
    FROM python:3.11-slim

    # ----
    # Etapa 2: Configuración del Entorno
    # ----
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1
    
    # ----
    # Etapa 3: Preparación del Espacio de Trabajo
    # ----
    WORKDIR /app
    

    RUN apt-get update && apt-get install -y build-essential pkg-config default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

    # ----
    # Etapa 4: Instalación de Dependencias (El paso más importante para la eficiencia)
    # ----
    COPY requirements.txt .
    RUN pip install -r requirements.txt
    
    # ----
    # Etapa 5: Copia del Código de la Aplicación
    # ----
    COPY . .
    
    # ----
    # Etapa 6: Comando de Ejecución
    # ----
    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
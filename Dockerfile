# Dockerfile – FUNCIONA EN 2025 con python:3.13-slim
FROM python:3.13-slim

# Evita preguntas al instalar paquetes
ENV DEBIAN_FRONTEND=noninteractive

# INSTALA LAS DEPENDENCIAS CORRECTAS (el paquete viejo ya no existe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    libgtk-3-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copia el script
COPY ping.py .

# Instala dependencias Python con uv (rápido y limpio)
RUN pip install --no-cache-dir uv && \
    uv pip install --system matplotlib numpy requests openpyxl

# Ejecuta el monitor
CMD ["python", "ping.py"]
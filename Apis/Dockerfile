# Usa una imagen base de Python con Debian Bullseye (Debian 11) o Bookworm (Debian 12), ya que Buster (Debian 10) ha llegado a EOL.
# Esto asegura que los repositorios apt-get estén activos.
FROM python:3.10-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema operativo necesarias:
# - build-essential, cmake, libopenblas-dev, liblapack-dev (para dlib/face_recognition)
# - libjpeg-dev, libpng-dev, libtiff-dev, libavcodec-dev, libavformat-dev, libswscale-dev (para OpenCV)
# - unixodbc-dev, curl, gnupg (para pyodbc y la instalación del driver ODBC de MS)
# - libgl1 (para resolver ImportError: libGL.so.1)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    unixodbc-dev \
    curl \
    gnupg \
    libgl1 && \
    # Limpia el caché de apt para reducir el tamaño de la imagen
    rm -rf /var/lib/apt/lists/*

# Instala el driver ODBC 17 para SQL Server (recomendado y robusto)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    # Limpia el caché de apt después de la instalación del driver
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configuración de unixODBC para encontrar el driver (CRÍTICO para IM002)
# Esto asegura que el Driver Manager sepa dónde está el driver de SQL Server
RUN echo "[ODBC Driver 17 for SQL Server]\nDescription=Microsoft ODBC Driver 17 for SQL Server\nDriver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.so\nUsageCount=1" >> /etc/odbcinst.ini && \
    echo "[msodbcsql17]\nDescription=Microsoft ODBC Driver 17 for SQL Server\nDriver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.so\nUsageCount=1" >> /etc/odbcinst.ini

# Copia el archivo requirements.txt y luego instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código de la aplicación al contenedor
# Asegúrate de que app.py y gunicorn_conf.py estén en el mismo directorio.
COPY . .

# Expone el puerto que tu aplicación Flask utilizará (Gunicorn lo usará)
# Azure App Service esperará que tu aplicación escuche en el puerto definido por la variable de entorno PORT
EXPOSE 5000

# Define la variable de entorno PORT que Azure App Service espera
ENV PORT 5000

# Comando para ejecutar la aplicación con Gunicorn
# Usamos el hook post_worker_init para cargar los rostros.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]

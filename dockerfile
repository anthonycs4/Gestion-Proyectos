# Usa una imagen base de Python
FROM python:3.11-slim

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
  default-libmysqlclient-dev \
  build-essential \
  pkg-config \
  libssl-dev \
  libffi-dev

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del proyecto al contenedor
COPY . .

# Expone el puerto
EXPOSE 5000

# Establece las variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Comando para ejecutar la aplicación Flask en modo desarrollo escuchando en 0.0.0.0
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

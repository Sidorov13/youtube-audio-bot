FROM python:3.11-slim

# Установка ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Создание рабочей директории
WORKDIR /app

# Копирование файлов в контейнер
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск приложения
CMD ["python", "main.py"]

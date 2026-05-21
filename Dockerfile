FROM python:3.11-slim

WORKDIR /app

# Avval kutubxonalarni o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Hamma fayllarni /app papkasi ichiga nusxalaymiz
COPY . /app

# Bot aynan shu papkadan ishga tushishini majburlaymiz
CMD ["python", "/app/main.py"]
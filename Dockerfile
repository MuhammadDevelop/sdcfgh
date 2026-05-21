# 1. Serverga rasmiy kichik hajmli Python muhitini yuklashni aytamiz
FROM python:3.11-slim

# 2. Virtual server ichida loyiha ishlaydigan asosiy papkani belgilaymiz
WORKDIR /app

# 3. requirements.txt faylini virtual muhitga nusxalaymiz
COPY requirements.txt .

# 4. Kutubxonalarni virtual muhit ichiga o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kompyuteringizdagi qolgan barcha kodlarni (main.py va h.k.) virtual muhitga ko'chiramiz
COPY . .

# 6. Server ishga tushganda botni qaysi buyruq orqali yurgizishni buyuramiz
CMD ["python", "main.py"]
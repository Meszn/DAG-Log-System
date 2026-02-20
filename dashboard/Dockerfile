# Hafif Python sürümü
FROM python:3.10-slim

# Çalışma klasörü
WORKDIR /app

# Gereksinimleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Streamlit portunu dışarı aç
EXPOSE 8501

# Uygulamayı başlat
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# 🌌 DAG Centralized Log & Anomaly Monitoring System

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

Doğu Anadolu Gözlemevi (DAG) altyapısındaki servislerden gelen logları merkezi olarak toplayan, asenkron olarak işleyen ve **Machine Learning (Isolation Forest)** algoritmaları ile anormallikleri gerçek zamanlı tespit eden kurumsal düzeyde bir izleme (monitoring) sistemidir.

##  Özellikler

* **Asenkron Mimari:** Yüksek trafikli log akışları için `FastAPI` ve `Asyncpg` (PostgreSQL) entegrasyonu.
* **Yapay Zeka Destekli Anomali Tespiti:** Sistem kaynaklarındaki (CPU/RAM) aykırı durumları yakalamak için eğitilmiş `Isolation Forest` modeli.
* **Gerçek Zamanlı Log Shipper:** Sunuculardaki fiziksel log dosyalarını (örn: `application.log`) `tail -f` mantığıyla okuyup API'ye aktaran özel Python ajanı.
* **Cyberpunk Command Center:** `Streamlit` ve `Plotly` ile geliştirilmiş, karanlık temalı, hareketli kadranlara ve radar grafiklerine sahip interaktif gösterge paneli.
* **Clean Architecture:** Kolay ölçeklenebilir ve bakımı yapılabilir katmanlı proje yapısı.
* **Konteynerizasyon:** Tüm sistem (Database, Backend, Frontend) tek bir `docker-compose` komutuyla ayağa kalkar.

## 🏗️ Mimari Yapı

```text
dag-log-system/
│
├── app/                  # FastAPI Backend Servisi
│   ├── models/           # SQLAlchemy Veritabanı Modelleri
│   ├── routers/          # API Uç Noktaları (Endpoints)
│   ├── schemas/          # Pydantic Veri Doğrulama Şemaları
│   ├── services/         # ML Modelleri ve İş Mantığı
│   ├── config.py         # Ortam Değişkenleri
│   └── main.py           # Uygulama Başlangıç Noktası
│
├── dashboard/            # Streamlit Frontend Servisi
│   ├── app.py            # Arayüz ve Grafikler
│   └── Dockerfile
│
├── real_log_shipper.py   # Gerçek Zamanlı Log Okuyucu Ajan
├── train_real_model.py   # Gerçekçi Veri Seti Üretici ve Model Eğitici
├── docker-compose.yml    # Konteyner Orkestrasyonu
└── requirements.txt      # Bağımlılıklar
``` 
## 🛠️ Kurulum ve Çalıştırma
### 1. Ön Koşullar
Sisteminizde Docker ve Docker Compose kurulu olmalıdır.

### 2. Projeyi Klonlayın
```
bash
git clone [https://github.com/KULLANICI_ADIN/dag-log-system.git](https://github.com/KULLANICI_ADIN/dag-log-system.git)
cd dag-log-system
``` 
### 3. Çevresel Değişkenleri Ayarlayın (.env)
Ana dizinde bir .env dosyası oluşturun:

```
bash
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/dag_logs
SECRET_KEY=super_secret_key
``` 
### 4. Sistemi Ayağa Kaldırın
```
bash
docker-compose up --build
``` 
Bu komut şunları başlatacaktır:
- API (Swagger UI): http://localhost:8000/docs
- Dashboard: http://localhost:8501

## 📡 Canlı Log Akışını Test Etme
- Sistem ayağa kalktıktan sonra, logların arayüze düşmesi için Log Shipper'ı başlatın:
- Yeni bir terminal açın ve gerekli kütüphaneleri yükleyin (pip install requests).
Ajanı çalıştırın:

```
bash
python real_log_shipper.py
``` 
Başka bir terminalden application.log dosyasına veri yazarak anormallik sistemini test edin:

Normal Log Örneği:
```
bash
Add-Content application.log "[INFO] Service:Telescope CPU:25.5 MEM:40.0 Msg:Sistem stabil."
``` 
Anomali (Kritik) Log Örneği:

```
bash
Add-Content application.log "[ERROR] Service:Database CPU:99.9 MEM:95.0 Msg:Memory Leak tespit edildi!"
``` 
## 👨‍💻 Geliştirici
Mustafa Sezen - Software Engineering Student | AI & Data Science Enthusiast

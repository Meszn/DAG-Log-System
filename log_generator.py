import requests
import time
import random

API_URL = "http://localhost:8000/api/v1/logs/"

services = ["telescope-control", "dome-rotation", "weather-station", "data-archive"]
hosts = ["server-alpha", "server-beta", "server-gamma"]
levels = ["INFO", "WARNING", "ERROR", "DEBUG"]

print("🚀 Log Simülatörü Başlatılıyor... (Durdurmak için CTRL+C)")

while True:
    try:
        # %10 ihtimalle ANORMAL veri üret (Yüksek CPU/RAM)
        if random.random() < 0.10:
            cpu = random.uniform(80, 100)  # Çok yüksek CPU
            memory = random.uniform(80, 100)  # Çok yüksek RAM
            level = "ERROR"
            message = "CRITICAL: Kaynak tuketimi asiri yuksek! Sistem tikanabilir."
            print(f"⚠️  ANOMALİ Gönderiliyor! CPU: {cpu:.1f}")
        else:
            # Normal veri
            cpu = random.uniform(10, 40)
            memory = random.uniform(20, 50)

            level = random.choice(levels)
            message = "Rutin islem kontrolu yapildi."
            print(f"✅ Normal Log: CPU: {cpu:.1f}")

        log_data = {
            "host": random.choice(hosts),
            "service": random.choice(services),
            "level": level,
            "message": message,
            "cpu_usage": cpu,
            "memory_usage": memory
        }

        # API'ye gönder
        response = requests.post(API_URL, json=log_data)

        # Hata varsa yazdır
        if response.status_code != 200:
            print(f"❌ HATA: {response.text}")

        # Biraz bekle (Saniyede 2 log)
        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Simülasyon durduruldu.")
        break
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        time.sleep(2)
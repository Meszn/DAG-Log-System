import time
import requests
import re
import os

# --- AYARLAR ---
LOG_FILE_PATH = "application.log"
API_URL = "http://localhost:8000/api/v1/logs/"
HOSTNAME = "DAG-SERVER-PROD-01"

# --- REGEX ---
LOG_PATTERN = re.compile(
    r"\[(?P<level>\w+)\] Service:(?P<service>[\w-]+) CPU:(?P<cpu>\d+\.?\d*) MEM:(?P<mem>\d+\.?\d*) Msg:(?P<message>.*)")


def follow_windows_friendly(file_path):
    """
    Windows için dosya kilitlemeyen takip mekanizması (Düzeltilmiş).
    Dosyayı okur, KAPATIR ve sonra bekler.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")

    # Konum takibi
    current_position = 0
    # İlk açılışta dosyanın sonuna git
    with open(file_path, 'r') as f:
        f.seek(0, 2)
        current_position = f.tell()

    while True:
        has_new_data = False
        try:
            with open(file_path, 'r') as f:
                f.seek(current_position)
                lines = f.readlines()  # Tek tek değil, hepsini oku

                if lines:
                    current_position = f.tell()  # Yeni konumu kaydet
                    has_new_data = True

            # DOSYA ŞU AN KAPALI (WITH BLOĞUNDAN ÇIKTIK)

            if has_new_data:
                for line in lines:
                    yield line
            else:
                # Dosya kapalıyken bekle ki PowerShell yazabilsin
                time.sleep(1)

        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(1)


def parse_and_send(line):
    line = line.strip()
    if not line: return

    match = LOG_PATTERN.search(line)
    if match:
        data = match.groupdict()

        payload = {
            "host": HOSTNAME,
            "service": data["service"],
            "level": data["level"],
            "message": data["message"].strip(),
            "cpu_usage": float(data["cpu"]),
            "memory_usage": float(data["mem"])
        }

        try:
            resp = requests.post(API_URL, json=payload)
            if resp.status_code == 200:
                is_anomaly = resp.json().get('is_anomaly')
                status_icon = "🚨 ANOMALİ!" if is_anomaly else "✅"
                print(f"{status_icon} Gönderildi: {payload['message']}")
            else:
                print(f"❌ API Hatası: {resp.status_code}")
        except Exception as e:
            print(f"❌ Bağlantı Koptu: {e}")


if __name__ == "__main__":
    print(f"👀 Gözlem Başladı (Windows Modu - Kilit Sorunu Giderildi): {LOG_FILE_PATH}")

    try:
        for line in follow_windows_friendly(LOG_FILE_PATH):
            parse_and_send(line)
    except KeyboardInterrupt:
        print("\n🛑 İzleme durduruldu.")
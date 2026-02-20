import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Ayarlar
DATA_FILE = "server_metrics.csv"
MODEL_PATH = "app/services/dag_model.pkl"
SCALER_PATH = "app/services/dag_scaler.pkl"


def generate_realistic_data(n_samples=5000):
    """
    Gerçek bir sunucunun 1 haftalık CPU/RAM davranışını simüle eder.
    """
    print("📊 Gerçekçi veri seti oluşturuluyor...")

    # Zaman serisi (dakika dakika)
    time_index = np.arange(n_samples)

    # 1. GÜNLÜK DÖNGÜ (Day/Night Cycle): Sunucular gündüz yoğun, gece sakindir.
    # Sinüs dalgası kullanarak günlük yükü simüle ediyoruz.
    daily_cycle = np.sin(time_index * 2 * np.pi / (24 * 60))

    # 2. CPU OLUŞTURMA
    # Baz Yük (%20) + Günlük Döngü Etkisi (%30) + Rastgele Gürültü (%10)
    cpu_usage = 20 + (daily_cycle * 15) + np.random.normal(0, 5, n_samples)
    cpu_usage = np.clip(cpu_usage, 5, 100)  # 0-100 arasına sabitle

    # 3. RAM OLUŞTURMA
    # Baz Yük (%40) + CPU ile hafif korelasyon + Rastgele Gürültü
    memory_usage = 40 + (cpu_usage * 0.5) + np.random.normal(0, 2, n_samples)
    memory_usage = np.clip(memory_usage, 10, 100)

    # DataFrame oluştur
    df = pd.DataFrame({
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage
    })

    # 4. ANOMALİ ENJEKSİYONU (Gerçek Saldırılar)
    # Sisteme %2 oranında anormallik (aşırı yük veya çökme) ekleyelim
    n_anomalies = int(n_samples * 0.02)
    indices = np.random.choice(n_samples, n_anomalies, replace=False)

    for i in indices:
        scenario = np.random.choice(['spike', 'leak', 'crash'])

        if scenario == 'spike':  # Ani CPU Patlaması (DDoS vb.)
            df.loc[i, 'cpu_usage'] = np.random.uniform(90, 100)
            df.loc[i, 'memory_usage'] = np.random.uniform(50, 80)

        elif scenario == 'leak':  # Memory Leak (RAM şişmesi)
            df.loc[i, 'cpu_usage'] = np.random.uniform(20, 40)
            df.loc[i, 'memory_usage'] = np.random.uniform(95, 100)

        elif scenario == 'crash':  # Sistem Çökmesi (Ani düşüş)
            df.loc[i, 'cpu_usage'] = 0.0
            df.loc[i, 'memory_usage'] = 0.0

    print(f"✅ {n_samples} satırlık veri seti '{DATA_FILE}' olarak kaydedildi.")
    df.to_csv(DATA_FILE, index=False)
    return df


def train_model():
    # 1. Veriyi Yükle
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = generate_realistic_data()

    print("🧠 Model eğitimi başlıyor...")

    # 2. Ölçeklendirme (Scaling) - ÇOK ÖNEMLİ
    # CPU 100, RAM 16000 olabilir. Bunları aynı düzleme (0-1 arası veya standart sapma) getirmeliyiz.
    scaler = StandardScaler()
    X_train = scaler.fit_transform(df[['cpu_usage', 'memory_usage']])

    # 3. Isolation Forest Eğitimi
    # contamination=0.02 -> Verinin %2'sinin kirli (anomali) olduğunu biliyoruz.
    model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
    model.fit(X_train)

    # 4. Kaydetme (Hem Modeli Hem Scaler'ı kaydetmeliyiz!)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)  # Scaler'ı unutursak gelen veriyi normalize edemeyiz!

    print(f"🎉 Başarılı! Model: {MODEL_PATH}, Scaler: {SCALER_PATH}")
    print("Şimdi backend servisini yeniden başlat.")


if __name__ == "__main__":
    train_model()
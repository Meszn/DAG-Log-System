import numpy as np
import joblib
import os


class AnomalyDetector:
    def __init__(self):
        self.model_path = "app/services/dag_model.pkl"
        self.scaler_path = "app/services/dag_scaler.pkl"
        self.model = None
        self.scaler = None
        self.load_artifacts()

    def load_artifacts(self):
        """Modeli ve Scaler'ı diskten yükler"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print(f"✅ ML Modeli ve Scaler Yüklendi.")
            except Exception as e:
                print(f"❌ Yükleme hatası: {e}")
                self.model = None
        else:
            print(f"⚠️ Dosyalar eksik! Lütfen 'train_real_model.py' çalıştırın.")

    def predict(self, cpu: float, memory: float):
        if not self.model or not self.scaler:
            return 0.0, False

        # 1. Veriyi Hazırla
        raw_data = np.array([[cpu, memory]])

        # 2. Veriyi Ölçeklendir (Eğitimdeki standartlara getir)
        scaled_data = self.scaler.transform(raw_data)

        # 3. Tahmin Yap
        score = self.model.decision_function(scaled_data)[0]
        prediction = self.model.predict(scaled_data)[0]

        is_anomaly = True if prediction == -1 else False
        return float(score), is_anomaly


# Singleton Instance
ml_service = AnomalyDetector()
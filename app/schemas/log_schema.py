from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Log oluştururken istenecek veriler
class LogCreate(BaseModel):
    host: str
    service: str
    level: str
    message: str
    cpu_usage: float
    memory_usage: float

# Kullanıcıya dönecek veri formatı
class LogResponse(LogCreate):
    id: int
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool

    model_config = ConfigDict(from_attributes=True)
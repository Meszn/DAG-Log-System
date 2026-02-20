from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    host = Column(String, index=True)
    service = Column(String, index=True)
    level = Column(String, index=True)
    message = Column(Text)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)

    # ML Tahmin Sonuçları
    anomaly_score = Column(Float)
    is_anomaly = Column(Boolean, default=False)
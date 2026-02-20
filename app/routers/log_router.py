from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.schemas.log_schema import LogCreate, LogResponse
from app.models.log_model import Log
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])

# 1. LOG KAYDETME (POST)
@router.post("/", response_model=LogResponse)
async def create_log(log_in: LogCreate, db: AsyncSession = Depends(get_db)):
    # ML Analizi
    score, is_anomaly = ml_service.predict(log_in.cpu_usage, log_in.memory_usage)

    new_log = Log(
        host=log_in.host,
        service=log_in.service,
        level=log_in.level,
        message=log_in.message,
        cpu_usage=log_in.cpu_usage,
        memory_usage=log_in.memory_usage,
        anomaly_score=score,
        is_anomaly=is_anomaly
    )

    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log

# 2. LOGLARI OKUMA (GET) - YENİ EKLENEN KISIM
@router.get("/", response_model=List[LogResponse])
async def read_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # Veritabanından son kayıtları çek (Zamana göre tersten sıralı)
    query = select(Log).order_by(Log.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs
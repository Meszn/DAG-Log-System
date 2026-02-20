from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import log_router

# Uygulama başlarken tabloları oluştur
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="DAG Log & Anomaly System",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(log_router.router)

@app.get("/")
async def root():
    return {"message": "DAG Log System is Running 🚀"}
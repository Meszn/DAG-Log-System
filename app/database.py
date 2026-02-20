from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Veritabanı Motoru (Async)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Oturum Oluşturucu
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency Injection (Her istekte DB aç/kapat)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
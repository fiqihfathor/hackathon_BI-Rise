from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv

import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SYNC_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ✅ Sync engine & session
sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
    

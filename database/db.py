import logging
from typing import AsyncGenerator, Optional
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shadow_system.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./shadow_system.db")

# Async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

# Create session factory
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("✅ Database initialized")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_db():
    """Context manager for database session"""
    async with async_session() as session:
        yield session


def get_sync_session() -> Session:
    """Get sync database session (for Celery tasks)"""
    sync_engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
    return SessionLocal()


class DBManager:
    """Database manager for common operations"""
    
    def __init__(self):
        self.async_engine = async_engine
        self.async_session = async_session
    
    async def health_check(self) -> bool:
        """Check database connection"""
        try:
            async with async_session() as session:
                await session.exec("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


db_manager = DBManager()

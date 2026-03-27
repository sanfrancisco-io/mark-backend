import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://marketplace:secret@localhost:5432/marketplace")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


def make_test_session_factory(url: str) -> async_sessionmaker:
    """Create a session factory backed by a NullPool engine — safe for test isolation."""
    test_engine = create_async_engine(url, poolclass=NullPool)
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

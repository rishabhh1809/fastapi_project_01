from collections.abc import Callable
from typing import AsyncGenerator, Optional, Any, Type, List
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import Select

from app.settings import get_settings

settings = get_settings()

Base = declarative_base()

# ------------------------------------------ Database Engine & Session ------------------------------------------

db_engine = create_async_engine(
    settings.db.db_url,
    echo=settings.db.db_echo,
    pool_pre_ping=True,
    pool_size=settings.db.db_pool_size,
    max_overflow=settings.db.db_max_overflow,
)

DBAsyncSession: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=db_engine, class_=AsyncSession, expire_on_commit=False
)

# ------------------------------------------ Async Session Dependencies ------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with DBAsyncSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():

    await db_engine.dispose()


# ------------------------------------------ Session Factory ------------------------------------------


def get_session_factory(db_name: Optional[str] = None) -> Callable[[], AsyncSession]:
    """Get session factory. Extensible for multi-database support."""
    return DBAsyncSession


# ------------------------------------------ Generic CRUD Utilities ------------------------------------------


async def create(instance: Any, db_name: Optional[str] = None) -> int:
    """Create a new record and return its ID."""
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                session.add(instance)
                await session.flush()
                return instance.id
        except Exception:
            await session.rollback()
            raise


async def update(instance: Any, db_name: Optional[str] = None) -> int:
    """Update an existing record and return its ID."""
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                await session.merge(instance)
                await session.flush()
                return instance.id
        except Exception:
            await session.rollback()
            raise


async def update_fields(
    model: Type[Any], id: int, data: dict, db_name: Optional[str] = None
) -> int:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                instance = await session.get(model, id)
                if not instance:
                    raise ValueError(f"{model.__name__} with id {id} not found")
                for key, value in data.items():
                    setattr(instance, key, value)
                await session.flush()
                return instance.id
        except Exception:
            await session.rollback()
            raise


async def delete(instance: Any, db_name: Optional[str] = None) -> None:
    """Delete a record."""
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                await session.delete(instance)
        except Exception:
            await session.rollback()
            raise


async def delete_by_id(
    model: Type[Any], id: int, db_name: Optional[str] = None
) -> None:
    """Delete a record by ID."""
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        try:
            async with session.begin():
                stmt = sa_delete(model).where(model.id == id)
                await session.execute(stmt)
        except Exception:
            await session.rollback()
            raise


async def fetch_one(query: Select, db_name: Optional[str] = None) -> Optional[Any]:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def fetch_all(query: Select, db_name: Optional[str] = None) -> List[Any]:
    session_factory = get_session_factory(db_name)
    async with session_factory() as session:
        result = await session.execute(query)
        return list(result.scalars().all())

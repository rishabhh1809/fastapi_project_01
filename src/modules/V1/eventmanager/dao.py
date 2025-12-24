from typing import Optional, Any
from sqlalchemy import select, func

from app.database import (
    fetch_one,
    fetch_all,
    fetch_scalar,
    create,
    update,
    delete_by_id,
)
from .models import Event


class EventDAO:
    # -------------------- Read Operations --------------------

    @staticmethod
    async def get_by_id(event_id: int) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id)
        return await fetch_one(query)

    @staticmethod
    async def get_by_title(title: str) -> Optional[Event]:
        query = select(Event).where(Event.title == title)
        return await fetch_one(query)

    @staticmethod
    async def filter(**filters: Any) -> list[Event]:
        query = select(Event)

        skip = filters.pop("skip", 0)
        limit = filters.pop("limit", 100)

        conditions = []
        for key, value in filters.items():
            if hasattr(Event, key) and value is not None:
                conditions.append(getattr(Event, key) == value)

        if conditions:
            query = query.where(*conditions)

        query = query.offset(skip).limit(limit)
        return await fetch_all(query)

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> list[Event]:
        query = select(Event).offset(skip).limit(limit)
        return await fetch_all(query)

    @staticmethod
    async def get_available(skip: int = 0, limit: int = 100) -> list[Event]:
        query = select(Event).where(Event.available_seats > 0).offset(skip).limit(limit)
        return await fetch_all(query)

    # -------------------- Count Operations --------------------

    @staticmethod
    async def count_all() -> int:
        query = select(func.count(Event.id))
        return await fetch_scalar(query)

    @staticmethod
    async def count_available() -> int:
        query = select(func.count(Event.id)).where(Event.available_seats > 0)
        return await fetch_scalar(query)

    # -------------------- Write Operations --------------------

    @staticmethod
    async def create_event(event_data: dict) -> int:
        model = Event(**event_data)
        return await create(model)

    @staticmethod
    async def update_event(event_id: int, event_data: dict) -> int:
        event_data["id"] = event_id
        model = Event(**event_data)
        return await update(model)

    @staticmethod
    async def delete_event(event_id: int) -> None:
        await delete_by_id(Event, id=event_id)

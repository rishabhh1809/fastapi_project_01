from typing import Optional, List, Any
from sqlalchemy import select

from app.database import fetch_one, fetch_all, create, update, delete_by_id
from .models import Event
from .schemas import EventBase


class EventDAO:
    @staticmethod
    async def get_by_id(event_id: int) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id)
        return await fetch_one(query)

    @staticmethod
    async def get_by_title(title: str) -> Optional[Event]:
        query = select(Event).where(Event.title == title)
        return await fetch_one(query)

    @staticmethod
    async def filter(**filters: Any) -> List[Event]:
        query = select(Event)

        # Handle pagination
        skip = filters.pop("skip", 0)
        limit = filters.pop("limit", 100)

        # Apply remaining filters
        conditions = []
        for key, value in filters.items():
            if hasattr(Event, key) and value is not None:
                conditions.append(getattr(Event, key) == value)

        if conditions:
            query = query.where(*conditions)

        query = query.offset(skip).limit(limit)
        return await fetch_all(query)

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[Event]:
        query = select(Event).offset(skip).limit(limit)
        return await fetch_all(query)

    @staticmethod
    async def get_available(skip: int = 0, limit: int = 100) -> List[Event]:
        query = select(Event).where(Event.available_seats > 0).offset(skip).limit(limit)
        return await fetch_all(query)

    @staticmethod
    async def create_event(event: EventBase) -> int:
        event_dict = event.model_dump()
        # Auto-set available_seats to total_seats on creation
        if "available_seats" not in event_dict or event_dict["available_seats"] is None:
            event_dict["available_seats"] = event_dict.get("total_seats", 0)

        model = Event(**event_dict)
        return await create(model)

    @staticmethod
    async def update_event(event: EventBase) -> int:
        model = Event(**event.model_dump())
        return await update(model)

    @staticmethod
    async def delete_event(event_id: int) -> None:
        await delete_by_id(Event, id=event_id)

    @staticmethod
    async def count_events() -> int:
        query = select(Event)
        events = await fetch_all(query)
        return len(events)

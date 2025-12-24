from .schemas import EventBase
from .dao import EventDAO


class EventService:

    @staticmethod
    async def save(**data) -> tuple[dict, int]:
        try:
            title = data.get("title")
            if title:
                existing = await EventDAO.get_by_title(title)
                if existing:
                    return {"message": "Event with this title already exists"}, 409

            # Validate and create schema
            event_model = EventBase(**data)
            event_dict = event_model.model_dump()

            # Business rule: Auto-set available_seats to total_seats on creation
            if event_dict.get("available_seats") is None:
                event_dict["available_seats"] = event_dict.get("total_seats", 0)

            event_id = await EventDAO.create_event(event_dict)
            return {"id": event_id}, 201
        except Exception as e:
            return {"message": str(e)}, 400

    @staticmethod
    async def filter(**filters) -> tuple[dict, int]:
        skip = filters.get("skip", 0)
        limit = filters.get("limit", 100)

        events = await EventDAO.filter(**filters)
        events_data = [EventBase.model_validate(e).model_dump() for e in events]

        total = await EventDAO.count_all()

        return {"items": events_data, "total": total, "skip": skip, "limit": limit}, 200

    @staticmethod
    async def get_by_id(**data) -> tuple[dict, int]:
        event_id = data.get("id")
        if not event_id:
            return {"message": "Missing 'id' parameter"}, 400

        event = await EventDAO.get_by_id(int(event_id))
        if not event:
            return {"message": f"Event with ID {event_id} not found"}, 404

        return EventBase.model_validate(event).model_dump(), 200

    @staticmethod
    async def get_available(**data) -> tuple[dict, int]:
        skip = int(data.get("skip", 0))
        limit = int(data.get("limit", 100))

        events = await EventDAO.get_available(skip=skip, limit=limit)
        events_data = [EventBase.model_validate(e).model_dump() for e in events]

        total = await EventDAO.count_available()

        return {
            "items": events_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }, 200

    @staticmethod
    async def update(**data) -> tuple[dict, int]:
        event_id = data.get("id")
        if not event_id:
            return {"message": "Missing 'id' parameter"}, 400

        # Check if event exists
        existing = await EventDAO.get_by_id(int(event_id))
        if not existing:
            return {"message": f"Event with ID {event_id} not found"}, 404

        # Merge existing data with updates
        existing_data = EventBase.model_validate(existing).model_dump()
        for key, value in data.items():
            if value is not None and key != "id":
                existing_data[key] = value

        # Business rule: If total_seats is updated, adjust available_seats proportionally
        if "total_seats" in data and data["total_seats"] is not None:
            seat_difference = data["total_seats"] - existing.total_seats
            new_available = existing.available_seats + seat_difference
            existing_data["available_seats"] = max(0, new_available)

        updated_id = await EventDAO.update_event(int(event_id), existing_data)
        return {"id": updated_id}, 200

    @staticmethod
    async def delete(**data) -> tuple[dict, int]:
        event_id = data.get("id")
        if not event_id:
            return {"message": "Missing 'id' parameter"}, 400

        # Check if event exists
        existing = await EventDAO.get_by_id(int(event_id))
        if not existing:
            return {"message": f"Event with ID {event_id} not found"}, 404

        await EventDAO.delete_event(int(event_id))
        return {"id": event_id}, 200

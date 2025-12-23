from .schemas import EventBase
from .dao import EventDAO


class EventService:
    @staticmethod
    async def save(**data):
        try:
            title = data.get("title")
            if title:
                existing = await EventDAO.get_by_title(title)
                if existing:
                    return {"message": "Event with this title already exists"}, 409

            event_model = EventBase(**data)
            event_id = await EventDAO.create_event(event_model)
            return {"id": event_id}, 201
        except Exception as e:
            return {"message": str(e)}, 400

    @staticmethod
    async def filter(**filters):
        skip = filters.get("skip", 0)
        limit = filters.get("limit", 100)

        events = await EventDAO.filter(**filters)
        events_data = [EventBase.model_validate(e).model_dump() for e in events]

        total = await EventDAO.count_events()

        return {"items": events_data, "total": total, "skip": skip, "limit": limit}, 200

    @staticmethod
    async def get_by_id(**data):
        event_id = data.get("id")
        if not event_id:
            return {"message": "Missing 'id' parameter"}, 400

        event = await EventDAO.get_by_id(int(event_id))
        if not event:
            return {"message": f"Event with ID {event_id} not found"}, 404

        return EventBase.model_validate(event).model_dump(), 200

    @staticmethod
    async def get_available(**data):
        skip = data.get("skip", 0)
        limit = data.get("limit", 100)

        events = await EventDAO.get_available(skip=int(skip), limit=int(limit))
        events_data = [EventBase.model_validate(e).model_dump() for e in events]

        return {
            "items": events_data,
            "total": len(events_data),
            "skip": skip,
            "limit": limit,
        }, 200

    @staticmethod
    async def update(**data):
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

        # If total_seats is updated, adjust available_seats
        if "total_seats" in data and data["total_seats"] is not None:
            seat_difference = data["total_seats"] - existing.total_seats
            new_available = existing.available_seats + seat_difference
            existing_data["available_seats"] = max(0, new_available)

        event_model = EventBase(**existing_data)
        event_model.id = int(event_id)

        updated_id = await EventDAO.update_event(event_model)
        return {"id": updated_id}, 200

    @staticmethod
    async def delete(**data):
        event_id = data.get("id")
        if not event_id:
            return {"message": "Missing 'id' parameter"}, 400

        # Check if event exists
        existing = await EventDAO.get_by_id(int(event_id))
        if not existing:
            return {"message": f"Event with ID {event_id} not found"}, 404

        await EventDAO.delete_event(int(event_id))
        return {"id": event_id}, 200

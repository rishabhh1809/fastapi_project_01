from .schemas import BookingBase
from .dao import BookingDAO
from modules.V1.eventmanager.dao import EventDAO


class BookingService:
    @staticmethod
    async def save(**data):
        event_id = data.get("event_id")
        user_id = data.get("user_id")
        quantity = data.get("quantity", 1)

        if not event_id:
            return {"message": "Missing 'event_id' parameter"}, 400
        if not user_id:
            return {"message": "Missing 'user_id' parameter"}, 400

        # Check if event exists
        event = await EventDAO.get_by_id(int(event_id))
        if not event:
            return {"message": f"Event with ID {event_id} not found"}, 404

        # Check for existing booking
        existing = await BookingDAO.check_user_booking_exists(user_id, int(event_id))
        if existing:
            return {"message": "You already have a booking for this event"}, 409

        # Create booking with row-level locking (critical for concurrency)
        booking_data, message = await BookingDAO.create_booking_with_lock(
            event_id=int(event_id),
            user_id=user_id,
            quantity=int(quantity),
        )

        if booking_data:
            return booking_data, 201

        # Determine error code based on message
        if "not found" in message.lower():
            return {"message": message}, 404
        elif "not enough seats" in message.lower():
            return {"message": message}, 409
        else:
            return {"message": message}, 400

    @staticmethod
    async def filter(**filters):
        user_id = filters.get("user_id")
        skip = int(filters.get("skip", 0))
        limit = int(filters.get("limit", 100))

        if user_id:
            bookings = await BookingDAO.get_by_user(user_id, skip=skip, limit=limit)
            total = await BookingDAO.count_by_user(user_id)
        else:
            bookings = await BookingDAO.get_all(skip=skip, limit=limit)
            total = await BookingDAO.count_all()

        bookings_data = [BookingBase.model_validate(b).model_dump() for b in bookings]

        return {
            "items": bookings_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }, 200

    @staticmethod
    async def get_by_id(**data):
        booking_id = data.get("id")
        user_id = data.get("user_id")

        if not booking_id:
            return {"message": "Missing 'id' parameter"}, 400

        booking = await BookingDAO.get_by_id(int(booking_id))
        if not booking:
            return {"message": f"Booking with ID {booking_id} not found"}, 404

        # Verify ownership if user_id provided
        if user_id and booking.user_id != user_id:
            return {"message": "Access denied"}, 403

        return BookingBase.model_validate(booking).model_dump(), 200

    @staticmethod
    async def cancel(**data):
        booking_id = data.get("id")
        user_id = data.get("user_id")

        if not booking_id:
            return {"message": "Missing 'id' parameter"}, 400
        if not user_id:
            return {"message": "Missing 'user_id' parameter"}, 400

        booking_data, message = await BookingDAO.cancel_booking_with_lock(
            booking_id=int(booking_id),
            user_id=user_id,
        )

        if booking_data:
            return booking_data, 200

        # Determine error code based on message
        if "not found" in message.lower():
            return {"message": message}, 404
        elif "only cancel your own" in message.lower():
            return {"message": message}, 403
        elif "already cancelled" in message.lower():
            return {"message": message}, 409
        else:
            return {"message": message}, 400

    @staticmethod
    async def get_by_event(**data):
        event_id = data.get("event_id")
        skip = int(data.get("skip", 0))
        limit = int(data.get("limit", 100))

        if not event_id:
            return {"message": "Missing 'event_id' parameter"}, 400

        bookings = await BookingDAO.get_by_event(int(event_id), skip=skip, limit=limit)
        total = await BookingDAO.count_by_event(int(event_id))

        bookings_data = [BookingBase.model_validate(b).model_dump() for b in bookings]

        return {
            "items": bookings_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }, 200

    @staticmethod
    async def get_all(**data):
        skip = int(data.get("skip", 0))
        limit = int(data.get("limit", 100))

        bookings = await BookingDAO.get_all(skip=skip, limit=limit)
        total = await BookingDAO.count_all()

        bookings_data = [BookingBase.model_validate(b).model_dump() for b in bookings]

        return {
            "items": bookings_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }, 200

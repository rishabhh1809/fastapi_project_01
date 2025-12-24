from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import execute_transaction
from .schemas import BookingBase
from .dao import BookingDAO
from .models import BookingStatus
from modules.V1.eventmanager.dao import EventDAO


class BookingService:
    # -------------------- Create Booking --------------------

    @staticmethod
    async def save(**data) -> tuple[dict, int]:
        """
        Create a new booking with proper validation and concurrency control.

        Business Rules:
        1. Event must exist
        2. User cannot have duplicate confirmed bookings for same event
        3. Sufficient seats must be available
        4. Seat count is atomically decremented
        """
        event_id = data.get("event_id")
        user_id = data.get("user_id")
        quantity = data.get("quantity", 1)

        # Validate required fields
        if not event_id:
            return {"message": "Missing 'event_id' parameter"}, 400
        if not user_id:
            return {"message": "Missing 'user_id' parameter"}, 400

        event_id = int(event_id)
        quantity = int(quantity)

        # Validate quantity
        if quantity < 1:
            return {"message": "Quantity must be at least 1"}, 400

        # Check if event exists (quick check before transaction)
        event = await EventDAO.get_by_id(event_id)
        if not event:
            return {"message": f"Event with ID {event_id} not found"}, 404

        # Check for existing confirmed booking
        existing = await BookingDAO.get_user_confirmed_booking(user_id, event_id)
        if existing:
            return {"message": "You already have a booking for this event"}, 409

        # Create booking with transaction and row-level locking
        booking_data, status_code = await BookingService._create_booking_transaction(
            event_id=event_id,
            user_id=user_id,
            quantity=quantity,
        )

        return booking_data, status_code

    @staticmethod
    async def _create_booking_transaction(
        event_id: int, user_id: str, quantity: int
    ) -> tuple[dict, int]:
        """
        Execute booking creation within a transaction with row-level locking.
        This ensures atomic seat reservation and prevents overbooking.
        """

        async def _operation(session: AsyncSession) -> tuple[dict, int]:
            # Lock the event row to prevent race conditions
            event = await BookingDAO.get_event_with_lock_in_session(session, event_id)

            if not event:
                return {"message": "Event not found"}, 404

            # Business rule: Check seat availability
            if event.available_seats < quantity:
                return {
                    "message": f"Not enough seats available. Requested: {quantity}, Available: {event.available_seats}"
                }, 409

            # Decrement available seats
            await BookingDAO.update_event_seats_in_session(session, event, -quantity)

            # Create the booking
            booking = await BookingDAO.create_in_session(
                session=session,
                event_id=event_id,
                user_id=user_id,
                quantity=quantity,
                status=BookingStatus.CONFIRMED,
            )

            return BookingService._booking_to_dict(booking), 201

        try:
            return await execute_transaction(_operation)
        except Exception as e:
            return {"message": f"Failed to create booking: {str(e)}"}, 500

    # -------------------- Cancel Booking --------------------

    @staticmethod
    async def cancel(**data) -> tuple[dict, int]:
        """
        Cancel a booking and restore available seats.

        Business Rules:
        1. Booking must exist
        2. User can only cancel their own bookings
        3. Cannot cancel already cancelled bookings
        4. Seats are atomically restored to event
        """
        booking_id = data.get("id")
        user_id = data.get("user_id")

        # Validate required fields
        if not booking_id:
            return {"message": "Missing 'id' parameter"}, 400
        if not user_id:
            return {"message": "Missing 'user_id' parameter"}, 400

        booking_id = int(booking_id)

        # Get booking for validation
        booking = await BookingDAO.get_by_id(booking_id)
        if not booking:
            return {"message": f"Booking with ID {booking_id} not found"}, 404

        # Business rule: Verify ownership
        if booking.user_id != user_id:
            return {"message": "You can only cancel your own bookings"}, 403

        # Business rule: Check if already cancelled
        if booking.status == BookingStatus.CANCELLED:
            return {"message": "Booking is already cancelled"}, 409

        # Execute cancellation with transaction
        booking_data, status_code = await BookingService._cancel_booking_transaction(
            booking_id=booking_id,
            event_id=booking.event_id,
            quantity=booking.quantity,
        )

        return booking_data, status_code

    @staticmethod
    async def _cancel_booking_transaction(
        booking_id: int, event_id: int, quantity: int
    ) -> tuple[dict, int]:
        """
        Execute booking cancellation within a transaction with row-level locking.
        This ensures atomic seat restoration.
        """

        async def _operation(session: AsyncSession) -> tuple[dict, int]:
            # Get booking within transaction
            booking = await BookingDAO.get_by_id_in_session(session, booking_id)
            if not booking:
                return {"message": "Booking not found"}, 404

            # Lock the event row
            event = await BookingDAO.get_event_with_lock_in_session(session, event_id)
            if not event:
                return {"message": "Associated event not found"}, 404

            # Update booking status
            booking = await BookingDAO.update_status_in_session(
                session, booking, BookingStatus.CANCELLED
            )

            # Restore available seats
            await BookingDAO.update_event_seats_in_session(session, event, quantity)

            return BookingService._booking_to_dict(booking), 200

        try:
            return await execute_transaction(_operation)
        except Exception as e:
            return {"message": f"Failed to cancel booking: {str(e)}"}, 500

    # -------------------- Read Operations --------------------

    @staticmethod
    async def get_by_id(**data) -> tuple[dict, int]:
        """Get a single booking by ID with optional ownership verification."""
        booking_id = data.get("id")
        user_id = data.get("user_id")

        if not booking_id:
            return {"message": "Missing 'id' parameter"}, 400

        booking = await BookingDAO.get_by_id(int(booking_id))
        if not booking:
            return {"message": f"Booking with ID {booking_id} not found"}, 404

        # Business rule: Verify ownership if user_id provided
        if user_id and booking.user_id != user_id:
            return {"message": "Access denied"}, 403

        return BookingBase.model_validate(booking).model_dump(), 200

    @staticmethod
    async def filter(**filters) -> tuple[dict, int]:
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
    async def get_by_event(**data) -> tuple[dict, int]:
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
    async def get_all(**data) -> tuple[dict, int]:
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

    # -------------------- Helper Methods --------------------

    @staticmethod
    def _booking_to_dict(booking: Any) -> dict:
        return {
            "id": booking.id,
            "event_id": booking.event_id,
            "user_id": booking.user_id,
            "quantity": booking.quantity,
            "status": booking.status.value,
        }

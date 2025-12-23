from typing import Optional, List, Tuple, Any
from sqlalchemy import select

from app.database import (
    fetch_one,
    fetch_all,
    get_session_factory,
)
from .models import Booking, BookingStatus
from modules.V1.eventmanager.models import Event


class BookingDAO:
    @staticmethod
    async def get_by_id(booking_id: int) -> Optional[Booking]:
        query = select(Booking).where(Booking.id == booking_id)
        return await fetch_one(query)

    @staticmethod
    async def filter(**filters: Any) -> List[Booking]:
        query = select(Booking)

        skip = filters.pop("skip", 0)
        limit = filters.pop("limit", 100)

        conditions = []
        for key, value in filters.items():
            if hasattr(Booking, key) and value is not None:
                conditions.append(getattr(Booking, key) == value)

        if conditions:
            query = query.where(*conditions)

        query = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit)
        return await fetch_all(query)

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[Booking]:
        query = (
            select(Booking)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return await fetch_all(query)

    @staticmethod
    async def get_by_user(
        user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        query = (
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return await fetch_all(query)

    @staticmethod
    async def get_by_event(
        event_id: int, skip: int = 0, limit: int = 100
    ) -> List[Booking]:
        query = (
            select(Booking)
            .where(Booking.event_id == event_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return await fetch_all(query)

    @staticmethod
    async def check_user_booking_exists(user_id: str, event_id: int) -> bool:
        query = select(Booking).where(
            Booking.user_id == user_id,
            Booking.event_id == event_id,
            Booking.status == BookingStatus.CONFIRMED,
        )
        result = await fetch_one(query)
        return result is not None

    @staticmethod
    async def create_booking_with_lock(
        event_id: int, user_id: str, quantity: int = 1
    ) -> Tuple[Optional[dict], str]:
        """
        Create a booking with row-level locking to prevent overbooking.

        CRITICAL IMPLEMENTATION:
        1. Lock the Event row using SELECT ... FOR UPDATE
        2. Check if available_seats >= requested quantity
        3. Decrement available_seats
        4. Create the booking record
        5. Commit happens at session level

        Returns:
            Tuple of (booking_dict or None, status message)
        """
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                async with session.begin():
                    # Step 1: Lock the event row for update
                    event_query = (
                        select(Event)
                        .where(Event.id == event_id)
                        .with_for_update()  # Row-level lock - critical for preventing race conditions
                    )
                    result = await session.execute(event_query)
                    event = result.scalar_one_or_none()

                    # Check if event exists
                    if not event:
                        return None, "Event not found"

                    # Step 2: Check available seats
                    if event.available_seats < quantity:
                        return (
                            None,
                            f"Not enough seats available. Requested: {quantity}, Available: {event.available_seats}",
                        )

                    # Step 3: Decrement available seats
                    event.available_seats -= quantity

                    # Step 4: Create booking
                    booking = Booking(
                        event_id=event_id,
                        user_id=user_id,
                        quantity=quantity,
                        status=BookingStatus.CONFIRMED,
                    )
                    session.add(booking)

                    # Flush to get the booking ID
                    await session.flush()
                    await session.refresh(booking)

                    # Return booking data
                    booking_data = {
                        "id": booking.id,
                        "event_id": booking.event_id,
                        "user_id": booking.user_id,
                        "quantity": booking.quantity,
                        "status": booking.status.value,
                    }
                    return booking_data, "Booking created successfully"
            except Exception as e:
                await session.rollback()
                return None, str(e)

    @staticmethod
    async def cancel_booking_with_lock(
        booking_id: int, user_id: str
    ) -> Tuple[Optional[dict], str]:
        """
        Cancel a booking and restore available seats with row-level locking.

        CRITICAL IMPLEMENTATION:
        1. Get the booking
        2. Lock the Event row using SELECT ... FOR UPDATE
        3. Update booking status to CANCELLED
        4. Increment available_seats
        5. Commit happens at session level

        Returns:
            Tuple of (booking_dict or None, status message)
        """
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                async with session.begin():
                    # Get booking
                    booking_query = select(Booking).where(Booking.id == booking_id)
                    result = await session.execute(booking_query)
                    booking = result.scalar_one_or_none()

                    if not booking:
                        return None, "Booking not found"

                    # Verify ownership
                    if booking.user_id != user_id:
                        return None, "You can only cancel your own bookings"

                    # Check if already cancelled
                    if booking.status == BookingStatus.CANCELLED:
                        return None, "Booking is already cancelled"

                    # Lock the event row
                    event_query = (
                        select(Event)
                        .where(Event.id == booking.event_id)
                        .with_for_update()
                    )
                    result = await session.execute(event_query)
                    event = result.scalar_one_or_none()

                    if not event:
                        return None, "Associated event not found"

                    # Update booking status
                    booking.status = BookingStatus.CANCELLED

                    # Restore available seats
                    event.available_seats += booking.quantity

                    await session.flush()
                    await session.refresh(booking)

                    # Return booking data
                    booking_data = {
                        "id": booking.id,
                        "event_id": booking.event_id,
                        "user_id": booking.user_id,
                        "quantity": booking.quantity,
                        "status": booking.status.value,
                    }
                    return booking_data, "Booking cancelled successfully"
            except Exception as e:
                await session.rollback()
                return None, str(e)

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        bookings = await BookingDAO.get_by_user(user_id, skip=0, limit=10000)
        return len(bookings)

    @staticmethod
    async def count_by_event(event_id: int) -> int:
        bookings = await BookingDAO.get_by_event(event_id, skip=0, limit=10000)
        return len(bookings)

    @staticmethod
    async def count_all() -> int:
        bookings = await BookingDAO.get_all(skip=0, limit=100000)
        return len(bookings)

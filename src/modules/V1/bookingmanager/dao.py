from typing import Optional, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import fetch_one, fetch_all, fetch_scalar
from .models import Booking, BookingStatus
from modules.V1.eventmanager.models import Event


class BookingDAO:
    # -------------------- Read Operations --------------------

    @staticmethod
    async def get_by_id(booking_id: int) -> Optional[Booking]:
        """Fetch a booking by its ID."""
        query = select(Booking).where(Booking.id == booking_id)
        return await fetch_one(query)

    @staticmethod
    async def filter(**filters: Any) -> list[Booking]:
        """Filter bookings by dynamic criteria."""
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
    async def get_all(skip: int = 0, limit: int = 100) -> list[Booking]:
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
    ) -> list[Booking]:
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
    ) -> list[Booking]:
        query = (
            select(Booking)
            .where(Booking.event_id == event_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return await fetch_all(query)

    @staticmethod
    async def get_user_confirmed_booking(
        user_id: str, event_id: int
    ) -> Optional[Booking]:
        query = select(Booking).where(
            Booking.user_id == user_id,
            Booking.event_id == event_id,
            Booking.status == BookingStatus.CONFIRMED,
        )
        return await fetch_one(query)

    # -------------------- Count Operations --------------------

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        query = select(func.count(Booking.id)).where(Booking.user_id == user_id)
        return await fetch_scalar(query)

    @staticmethod
    async def count_by_event(event_id: int) -> int:
        query = select(func.count(Booking.id)).where(Booking.event_id == event_id)
        return await fetch_scalar(query)

    @staticmethod
    async def count_all() -> int:
        query = select(func.count(Booking.id))
        return await fetch_scalar(query)

    # -------------------- Transactional Operations (within session context) --------------------

    @staticmethod
    async def get_by_id_in_session(
        session: AsyncSession, booking_id: int
    ) -> Optional[Booking]:
        query = select(Booking).where(Booking.id == booking_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_event_with_lock_in_session(
        session: AsyncSession, event_id: int
    ) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id).with_for_update()
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_in_session(
        session: AsyncSession,
        event_id: int,
        user_id: str,
        quantity: int,
        status: BookingStatus = BookingStatus.CONFIRMED,
    ) -> Booking:
        booking = Booking(
            event_id=event_id,
            user_id=user_id,
            quantity=quantity,
            status=status,
        )
        session.add(booking)
        await session.flush()
        await session.refresh(booking)
        return booking

    @staticmethod
    async def update_status_in_session(
        session: AsyncSession, booking: Booking, status: BookingStatus
    ) -> Booking:
        booking.status = status
        await session.flush()
        await session.refresh(booking)
        return booking

    @staticmethod
    async def update_event_seats_in_session(
        session: AsyncSession, event: Event, seat_change: int
    ) -> Event:
        event.available_seats += seat_change
        await session.flush()
        return event

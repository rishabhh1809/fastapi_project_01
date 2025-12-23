from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from modules.V1.bookingmanager.models import BookingStatus


class BookingBase(BaseModel):
    id: Optional[int] = None
    event_id: Optional[int] = Field(None, gt=0, description="Event ID to book")
    user_id: Optional[str] = None
    quantity: Optional[int] = Field(
        1, ge=1, le=10, description="Number of tickets to book"
    )
    status: Optional[BookingStatus] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = Field(None, description="Booking status")


class BookingResponse(BaseModel):
    id: int
    event_id: int
    user_id: str
    quantity: int
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingWithEventResponse(BookingResponse):
    event_title: Optional[str] = None
    event_date: Optional[datetime] = None
    event_venue: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class BookingResult(BaseModel):
    success: bool
    booking: Optional[BookingResponse] = None
    message: str

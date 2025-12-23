from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventBase(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Event title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Event description"
    )
    date: Optional[datetime] = Field(None, description="Event date and time")
    venue: Optional[str] = Field(None, max_length=255, description="Event venue")
    total_seats: Optional[int] = Field(None, gt=0, description="Total number of seats")
    available_seats: Optional[int] = Field(None, ge=0, description="Available seats")
    price: Optional[Decimal] = Field(None, ge=0, description="Ticket price")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Event description"
    )
    date: datetime = Field(..., description="Event date and time")
    venue: Optional[str] = Field(None, max_length=255, description="Event venue")
    total_seats: int = Field(..., gt=0, description="Total number of seats")
    price: Decimal = Field(..., ge=0, description="Ticket price")

    @field_validator("date")
    @classmethod
    def validate_future_date(cls, v: datetime) -> datetime:
        if v.replace(tzinfo=None) < datetime.now():
            raise ValueError("Event date must be in the future")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    date: Optional[datetime] = None
    venue: Optional[str] = Field(None, max_length=255)
    total_seats: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, ge=0)


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    date: datetime
    venue: Optional[str]
    total_seats: int
    available_seats: int
    price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)

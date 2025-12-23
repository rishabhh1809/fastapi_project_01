from fastapi import APIRouter

from modules.V1.eventmanager.routers import router as event_router
from modules.V1.bookingmanager.routers import booking_router


router = APIRouter()

router.include_router(event_router, prefix="/events", tags=["Events"])
router.include_router(booking_router, prefix="/bookings", tags=["Bookings"])

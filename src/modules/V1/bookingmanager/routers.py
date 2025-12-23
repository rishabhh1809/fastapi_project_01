from fastapi import APIRouter, Request, Depends, Query

from app.auth import verify_jwt_token, require_role
from app.utility import ApiResponse
from app.project_schemas import APIResponse
from modules.V1.bookingmanager.controller import (
    booking_controller,
    booking_detail_controller,
    admin_bookings_controller,
    event_bookings_controller,
)
from modules.V1.bookingmanager.api_docs import (
    bookings_handler,
    booking_detail_handler,
    admin_bookings_handler,
    event_bookings_handler,
)


booking_router = APIRouter()


@booking_router.get(
    "/all",
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=admin_bookings_handler["GET"]["summary"],
    description=admin_bookings_handler["GET"]["description"],
)
async def get_all_bookings(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    current_user: dict = Depends(require_role("admin")),
):
    return await admin_bookings_controller(request=request, auth_data=current_user)


@booking_router.get(
    "/event/{event_id}",
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=event_bookings_handler["GET"]["summary"],
    description=event_bookings_handler["GET"]["description"],
)
async def get_event_bookings(
    request: Request,
    event_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    current_user: dict = Depends(require_role("admin")),
):
    return await event_bookings_controller(
        request=request, event_id=event_id, auth_data=current_user
    )


@booking_router.api_route(
    "",
    methods=["GET", "POST"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=bookings_handler["GET"]["summary"],
    description=bookings_handler["GET"]["description"],
)
async def handle_bookings(
    request: Request,
    current_user: dict = Depends(verify_jwt_token),
):
    return await booking_controller(request=request, auth_data=current_user)


@booking_router.api_route(
    "/{booking_id}",
    methods=["GET", "DELETE"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=booking_detail_handler["GET"]["summary"],
    description=booking_detail_handler["GET"]["description"],
)
async def handle_booking_detail(
    request: Request,
    booking_id: int,
    current_user: dict = Depends(verify_jwt_token),
):
    return await booking_detail_controller(
        request=request, booking_id=booking_id, auth_data=current_user
    )

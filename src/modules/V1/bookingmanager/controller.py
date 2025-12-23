from fastapi import Request
from app.utility import ApiResponse, get_request_data
from .services import BookingService


# ------------------------ BOOKING CRUD CONTROLLER ------------------------
async def booking_controller(request: Request, auth_data: dict) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)

    user_id = auth_data.get("user_id")
    data.update({"user_id": user_id, "role": auth_data.get("role")})

    method = request.method

    match method:
        case "POST":
            result, status_code = await BookingService.save(**data)
            message = "Booking created successfully"

        case "GET":
            result, status_code = await BookingService.filter(**data)
            message = "Bookings fetched successfully"

        case _:
            return ApiResponse(
                content={
                    "status": "error",
                    "message": "Method not allowed",
                    "code": 405,
                    "data": None,
                },
                status_code=405,
            )

    if status_code >= 400:
        return ApiResponse(
            content={
                "status": "error",
                "message": result.get("message", message),
                "code": status_code,
                "data": None,
            },
            status_code=status_code,
        )

    return ApiResponse(
        content={
            "status": "success",
            "message": message,
            "code": status_code,
            "data": result,
        },
        status_code=status_code,
    )


# ------------------------ BOOKING DETAIL CONTROLLER ------------------------
async def booking_detail_controller(
    request: Request, booking_id: int, auth_data: dict
) -> ApiResponse:
    data = {
        "id": booking_id,
        "user_id": auth_data.get("user_id"),
        "role": auth_data.get("role"),
    }

    method = request.method

    match method:
        case "GET":
            result, status_code = await BookingService.get_by_id(**data)
            message = "Booking retrieved successfully"

        case "DELETE":
            result, status_code = await BookingService.cancel(**data)
            message = "Booking cancelled successfully"

        case _:
            return ApiResponse(
                content={
                    "status": "error",
                    "message": "Method not allowed",
                    "code": 405,
                    "data": None,
                },
                status_code=405,
            )

    if status_code >= 400:
        return ApiResponse(
            content={
                "status": "error",
                "message": result.get("message", "Error"),
                "code": status_code,
                "data": None,
            },
            status_code=status_code,
        )

    return ApiResponse(
        content={
            "status": "success",
            "message": message,
            "code": status_code,
            "data": result,
        },
        status_code=status_code,
    )


# ------------------------ ADMIN BOOKINGS CONTROLLER ------------------------
async def admin_bookings_controller(request: Request, auth_data: dict) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)

    match request.method:
        case "GET":
            result, status_code = await BookingService.get_all(**data)
            message = "All bookings fetched successfully"

        case _:
            return ApiResponse(
                content={
                    "status": "error",
                    "message": "Method not allowed",
                    "code": 405,
                    "data": None,
                },
                status_code=405,
            )

    return ApiResponse(
        content={
            "status": "success",
            "message": message,
            "code": status_code,
            "data": result,
        },
        status_code=status_code,
    )


# ------------------------ EVENT BOOKINGS CONTROLLER ------------------------
async def event_bookings_controller(
    request: Request, event_id: int, auth_data: dict
) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    data["event_id"] = event_id

    match request.method:
        case "GET":
            result, status_code = await BookingService.get_by_event(**data)
            message = "Event bookings fetched successfully"

        case _:
            return ApiResponse(
                content={
                    "status": "error",
                    "message": "Method not allowed",
                    "code": 405,
                    "data": None,
                },
                status_code=405,
            )

    return ApiResponse(
        content={
            "status": "success",
            "message": message,
            "code": status_code,
            "data": result,
        },
        status_code=status_code,
    )

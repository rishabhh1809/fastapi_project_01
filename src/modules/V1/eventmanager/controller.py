from typing import Optional
from fastapi import Request
from app.utility import ApiResponse, get_request_data
from .services import EventService


# ------------------------ EVENT CRUD CONTROLLER ------------------------
async def event_controller(
    request: Request, auth_data: Optional[dict] = None
) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)

    if auth_data:
        data["user_id"] = auth_data.get("user_id")
        data["role"] = auth_data.get("role")

    method = request.method

    match method:
        case "POST":
            result, status_code = await EventService.save(**data)
            message = "Event created successfully"

        case "GET":
            result, status_code = await EventService.filter(**data)
            message = "Events fetched successfully"

        case "DELETE":
            result, status_code = await EventService.delete(**data)
            message = "Event deleted successfully"

        case "PUT":
            result, status_code = await EventService.update(**data)
            message = "Event updated successfully"

        case _:
            return ApiResponse(
                content=ApiResponse.error(message="Method not allowed", code=405),
                status_code=405,
            )

    if status_code >= 400:
        return ApiResponse(
            content=ApiResponse.error(
                message=result.get("message", message), code=status_code
            ),
            status_code=status_code,
        )

    if status_code == 201:
        return ApiResponse(
            content=ApiResponse.created(data=result, message=message),
            status_code=status_code,
        )

    return ApiResponse(
        content=ApiResponse.success(data=result, message=message, code=status_code),
        status_code=status_code,
    )


# ------------------------ EVENT DETAIL CONTROLLER ------------------------
async def event_detail_controller(
    request: Request, event_id: int, auth_data: Optional[dict] = None
) -> ApiResponse:
    data: dict = {"id": event_id}

    if request.method in ["PUT", "PATCH"]:
        body_data = await get_request_data(
            request.headers.get("content-type", ""), request
        )
        data.update(body_data)

    if auth_data:
        data["user_id"] = auth_data.get("user_id")
        data["role"] = auth_data.get("role")

    method = request.method

    match method:
        case "GET":
            result, status_code = await EventService.get_by_id(**data)
            message = "Event retrieved successfully"

        case "PUT" | "PATCH":
            result, status_code = await EventService.update(**data)
            message = "Event updated successfully"

        case "DELETE":
            result, status_code = await EventService.delete(**data)
            message = "Event deleted successfully"

        case _:
            return ApiResponse(
                content=ApiResponse.error(message="Method not allowed", code=405),
                status_code=405,
            )

    if status_code >= 400:
        return ApiResponse(
            content=ApiResponse.error(
                message=result.get("message", "Error"), code=status_code
            ),
            status_code=status_code,
        )

    return ApiResponse(
        content=ApiResponse.success(data=result, message=message, code=status_code),
        status_code=status_code,
    )


# ------------------------ AVAILABLE EVENTS CONTROLLER ------------------------
async def available_events_controller(request: Request) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)

    match request.method:
        case "GET":
            result, status_code = await EventService.get_available(**data)
            message = "Available events fetched successfully"

        case _:
            return ApiResponse(
                content=ApiResponse.error(message="Method not allowed", code=405),
                status_code=405,
            )

    return ApiResponse(
        content=ApiResponse.success(data=result, message=message, code=status_code),
        status_code=status_code,
    )

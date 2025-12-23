from fastapi import APIRouter, Request, Depends
from app.project_schemas import APIResponse
from app.utility import ApiResponse
from app.auth import require_role

from .controller import (
    event_controller,
    event_detail_controller,
    available_events_controller,
)
from .api_docs import events_handler, event_detail_handler, available_events_handler

router = APIRouter()


# -------------------- AVAILABLE EVENTS (GET) --------------------
@router.api_route(
    "/available",
    methods=["GET"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=available_events_handler["GET"]["summary"],
    description=available_events_handler["GET"]["description"],
)
async def get_available_events(request: Request):
    return await available_events_controller(request)


# -------------------- LIST EVENTS (GET) --------------------
@router.api_route(
    "",
    methods=["GET"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=events_handler["GET"]["summary"],
    description=events_handler["GET"]["description"],
)
async def list_events(request: Request):
    return await event_controller(request)


# -------------------- CREATE EVENT (POST) --------------------
@router.api_route(
    "",
    methods=["POST"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=events_handler["POST"]["summary"],
    description=events_handler["POST"]["description"],
)
async def create_event(
    request: Request,
    auth_data: dict = Depends(require_role("admin")),
):
    return await event_controller(request, auth_data)


# -------------------- GET EVENT DETAIL (GET) --------------------
@router.api_route(
    "/{event_id}",
    methods=["GET"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=event_detail_handler["GET"]["summary"],
    description=event_detail_handler["GET"]["description"],
)
async def get_event(request: Request, event_id: int):
    return await event_detail_controller(request, event_id)


# -------------------- UPDATE EVENT (PUT) --------------------
@router.api_route(
    "/{event_id}",
    methods=["PUT"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=event_detail_handler["PUT"]["summary"],
    description=event_detail_handler["PUT"]["description"],
)
async def update_event(
    request: Request,
    event_id: int,
    auth_data: dict = Depends(require_role("admin")),
):
    return await event_detail_controller(request, event_id, auth_data)


# -------------------- PARTIAL UPDATE EVENT (PATCH) --------------------
@router.api_route(
    "/{event_id}",
    methods=["PATCH"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=event_detail_handler["PUT"]["summary"],
    description=event_detail_handler["PUT"]["description"],
)
async def partial_update_event(
    request: Request,
    event_id: int,
    auth_data: dict = Depends(require_role("admin")),
):
    return await event_detail_controller(request, event_id, auth_data)


# -------------------- DELETE EVENT (DELETE) --------------------
@router.api_route(
    "/{event_id}",
    methods=["DELETE"],
    response_model=APIResponse[dict],
    response_class=ApiResponse,
    summary=event_detail_handler["DELETE"]["summary"],
    description=event_detail_handler["DELETE"]["description"],
)
async def delete_event(
    request: Request,
    event_id: int,
    auth_data: dict = Depends(require_role("admin")),
):
    return await event_detail_controller(request, event_id, auth_data)

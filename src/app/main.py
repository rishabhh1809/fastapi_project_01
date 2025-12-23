import asyncio
import os
import sys
from contextlib import asynccontextmanager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvloop
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from prometheus_fastapi_instrumentator import Instrumentator

from app.settings import get_settings
from app.utility import exception_handler, ApiResponse
from app.project_schemas import APIResponse
from app.database import init_db, close_db
from app.routers import routers

# Set uvloop as the event loop policy for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

settings = get_settings()


# --------------------------------------------- Lifespan Context Manager ---------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print(
        f"🟢 {settings.app.project_name} v{settings.app.api_version} is starting up..."
    )
    print("📊 Database initialized")

    yield  # Application runs here

    # Shutdown
    await close_db()
    print("🔴 App is shutting down...")
    print("📊 Database connection closed")


# ------------------------------------------------ FastAPI App ----------------------------------------------
app = FastAPI(
    title=settings.app.project_name,
    description="High-performance Event Ticketing Platform API",
    version=settings.app.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --------------------------------------------- Prometheus Metrics ------------------------------------------
Instrumentator().instrument(app).expose(app, include_in_schema=False)

# ------------------------------------------------ Middleware -----------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
    allow_credentials=True,
)


# ----------------------------------------- Global Exception Handler ----------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    tb = await exception_handler(exc, request)
    response = APIResponse.error(
        message="Internal Server Error", code=HTTP_500_INTERNAL_SERVER_ERROR
    )
    if settings.app.debug:
        response.data = {"traceback": tb}
    return ApiResponse(content=response.model_dump())


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    response = APIResponse.error(message=str(exc.detail), code=exc.status_code)
    return ApiResponse(content=response.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = APIResponse.error(message="Validation Error", code=422)
    response.data = {"errors": exc.errors()}
    return ApiResponse(content=response.model_dump())


# -------------------------------------------------- Base Routes -------------------------------------------------
@app.get("/", tags=["Root"])
async def read_root():
    return ApiResponse.success(
        data={
            "name": settings.app.project_name,
            "version": settings.app.api_version,
            "docs": "/docs",
            "api": "/api/v1",
        },
        message="Welcome to the Event Ticketing Platform API",
    )


@app.get("/health", tags=["Monitoring"])
async def health_check():
    return ApiResponse.success(
        data={"status": "healthy", "version": settings.app.api_version},
        message="Service is running",
    )


# ------------------------------------------------- Routers -------------------------------------------------
routers(app)

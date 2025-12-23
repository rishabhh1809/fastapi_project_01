import sys
import httpx
import orjson
import asyncio
import traceback
from datetime import datetime, timezone
from typing import Optional, Any, Union, Generic, TypeVar, Dict, List
from fastapi import Request
from fastapi.responses import Response

from app.settings import get_settings

settings = get_settings()

# ------------------------------------------------------------ GLOBAL PROJECT TIME ----------------------------------------------


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


T = TypeVar("T")


class ApiResponse(Response, Generic[T]):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content)

    @staticmethod
    def success(
        data: Any = None, message: str = "Success", code: int = 200
    ) -> Dict[str, Any]:
        return {"code": code, "message": message, "status": "success", "data": data}

    @staticmethod
    def error(
        message: str = "An error occurred", code: int = 400, data: Any = None
    ) -> Dict[str, Any]:
        return {"code": code, "message": message, "status": "error", "data": data}

    @staticmethod
    def created(
        data: Any = None, message: str = "Resource created successfully"
    ) -> Dict[str, Any]:
        return ApiResponse.success(data=data, message=message, code=201)

    @staticmethod
    def not_found(
        message: str = "Resource not found", data: Any = None
    ) -> Dict[str, Any]:
        return ApiResponse.error(message=message, code=404, data=data)

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access", data: Any = None
    ) -> Dict[str, Any]:
        return ApiResponse.error(message=message, code=401, data=data)

    @staticmethod
    def forbidden(
        message: str = "Access forbidden", data: Any = None
    ) -> Dict[str, Any]:
        return ApiResponse.error(message=message, code=403, data=data)

    @staticmethod
    def conflict(
        message: str = "Resource conflict", data: Any = None
    ) -> Dict[str, Any]:
        return ApiResponse.error(message=message, code=409, data=data)

    @staticmethod
    def internal_error(
        message: str = "Internal server error", data: Any = None
    ) -> Dict[str, Any]:
        return ApiResponse.error(message=message, code=500, data=data)


async def exception_handler(
    e: Exception,
    request: Optional[Request] = None,
    data: Optional[Union[dict, str]] = None,
) -> str:
    """
    Handle exceptions and format traceback for logging.

    Args:
        e: The exception that was raised
        request: Optional FastAPI request object
        data: Optional additional data to log

    Returns:
        Formatted traceback string
    """
    tb_str = traceback.format_exception(type(e), e, e.__traceback__)
    tb_message = "".join(tb_str)
    request_data: Any = None

    if request:
        try:
            if request.method == "POST":
                request_data = await request.json()
            else:
                request_data = dict(request.query_params)
        except Exception as ex:
            request_data = f"<failed to extract request data: {ex}>"
    else:
        request_data = data

    print(
        "================================================================================"
    )
    if request:
        print("🚨 Source:\n", f"[{request.method}] {str(request.url)}")
    print("📦 Request data:\n", request_data)
    print("💥 An error occurred:\n", tb_message, file=sys.stderr)
    print(
        "================================== ERROR ======================================="
    )

    return tb_message


async def get_request_data(content_type: str, request: Request) -> Dict[str, Any]:
    """
    Extract request data from different sources based on content type.
    Handles JSON body, form data, and query parameters.

    Args:
        content_type: The Content-Type header value
        request: FastAPI request object

    Returns:
        Dictionary containing the request data
    """
    if request.method in ["GET", "DELETE"]:
        data: Dict[str, Any] = dict(request.query_params)
        if "id" in data:
            try:
                data["id"] = int(data["id"])
            except ValueError:
                raise ValueError("Query param 'id' must be an integer")
        return data
    else:
        if "application/json" in content_type:
            body = await request.body()
            return orjson.loads(body) if body else {}
        elif "multipart/form-data" in content_type:
            form = await request.form()
            return dict(form)
    raise ValueError(f"Unsupported Content-Type: {content_type}")


def convert_model_to_dict(model_instance: Any) -> Dict[str, Any]:
    if model_instance is None:
        return {}

    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        # Convert datetime objects to ISO format strings
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        result[column.name] = value
    return result


def convert_models_to_list(model_instances: List[Any]) -> List[Dict[str, Any]]:
    """Convert a list of SQLAlchemy model instances to a list of dictionaries."""
    return [convert_model_to_dict(instance) for instance in model_instances]


class HttpClient:
    """
    Usage Example:
        async with HttpClient(retries=3, timeout=10) as client:
            # GET request
            response = await client.get(
                "https://api.example.com/data",
                params={"key": "value"}
            )
            data = response.json()

        async with HttpClient() as client:
            # POST request
            response = await client.post(
                "https://api.example.com/create",
                json={"name": "John Doe", "email": "john@example.com"}
            )

    Parameters:
        retries (int): Number of retry attempts (default: 3)
        timeout (int): Timeout for requests in seconds (default: 10)

    Returns:
        httpx.Response: The HTTP response object
    """

    def __init__(self, retries: int = 3, timeout: int = 10):
        self.retries = retries
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        for attempt in range(1, self.retries + 1):
            try:
                resp = await self.client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except httpx.RequestError as e:
                wait_time = 2 ** (attempt - 1)
                print(
                    f"[Attempt {attempt}/{self.retries}] Network error: {e}. Retrying in {wait_time}s..."
                )
                if attempt < self.retries:
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    raise
                wait_time = 2 ** (attempt - 1)
                print(
                    f"[Attempt {attempt}/{self.retries}] API error: {e}. Retrying in {wait_time}s..."
                )
                if attempt < self.retries:
                    await asyncio.sleep(wait_time)
                else:
                    raise
        raise httpx.RequestError("Max retries exceeded")

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("PATCH", url, **kwargs)

    async def aclose(self):
        await self.client.aclose()

# /core/router.py
from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute
from typing import Callable
import json
from fastapi.responses import JSONResponse

# This import is correct and necessary
from .schemas import SuccessResponse

class StandardAPIRoute(APIRoute):
    """
    A custom APIRoute that automatically wraps successful responses in a
    standardized JSON envelope.
    """
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)

            # For successful responses (2xx status codes) that return JSON, wrap the content.
            # This excludes 204 No Content, which has no body.
            if (
                200 <= response.status_code < 300
                and response.status_code != 204
                and response.media_type == "application/json"
            ):
                # We need to get the raw body and re-wrap it
                try:
                    body = json.loads(response.body)
                except json.JSONDecodeError:
                    # This can happen if the response body is empty but content-type is json
                    body = None

                # Check if the body is already in the desired format to avoid double-wrapping
                if isinstance(body, dict) and body.get('status') == 'success':
                    return response

                # Wrap it in our standard SuccessResponse format
                return JSONResponse(
                    content=SuccessResponse(data=body).model_dump(by_alias=True),
                    status_code=response.status_code,
                    headers={k: v for k, v in dict(response.headers).items() if k.lower() != "content-length"},
                )

            # For errors, 204s, or non-JSON responses, return them as is
            return response

        return custom_route_handler


class StandardAPIRouter(APIRouter):
    """
    An APIRouter that uses the StandardAPIRoute class for all its routes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route_class = StandardAPIRoute

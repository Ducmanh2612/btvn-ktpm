
import os

import httpx
from fastapi import Request, HTTPException
from fastapi.responses import Response


USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://127.0.0.1:8001"
).rstrip("/")

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL",
    "http://127.0.0.1:8002"
).rstrip("/")


# Các headers không nên chuyển tiếp nguyên trạng
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
    "content-encoding",
}


async def _forward(
    request: Request,
    base_url: str,
    target_path: str
):
    # Giữ lại các headers cần thiết, bao gồm Authorization
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    # Giữ nguyên query parameters và request body
    body = await request.body()

    url = f"{base_url}/{target_path.lstrip('/')}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                content=body if body else None,
                headers=headers,
            )

        # Không chuyển tiếp các headers có thể không còn
        # phù hợp với body đã được httpx giải mã.
        response_headers = {
            key: value
            for key, value in upstream.headers.items()
            if key.lower() not in HOP_BY_HOP_HEADERS
        }

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=response_headers,
        )

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Upstream service timed out"
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Cannot connect to upstream service"
        ) from exc


async def forward_to_user(request: Request, path: str):
    # Login được chuyển tới /auth/login.
    # Các endpoint user được chuyển tới /users/...
    if path == "auth/login":
        target_path = "/auth/login"
    elif path:
        target_path = f"/users/{path}"
    else:
        target_path = "/users"

    return await _forward(
        request,
        USER_SERVICE_URL,
        target_path
    )


async def forward_to_order(request: Request, path: str):
    # Order service sử dụng các endpoint /order/...
    target_path = f"/order/{path}" if path else "/order"

    return await _forward(
        request,
        ORDER_SERVICE_URL,
        target_path
    )

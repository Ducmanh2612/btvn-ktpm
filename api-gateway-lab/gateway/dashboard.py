
import os
import asyncio
import httpx

from fastapi import Request, HTTPException

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://127.0.0.1:8001"
).rstrip("/")

ORDER_SERVICE_URL = os.getenv(
    "ORDER_SERVICE_URL",
    "http://127.0.0.1:8002"
).rstrip("/")


async def get_dashboard(request: Request):
    # Lấy thông tin user đã được xác thực bởi verify_jwt()
    user = getattr(request.state, "user", None)

    if isinstance(user, dict):
        username = user.get("username")
    else:
        username = getattr(user, "username", None)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="User identity not found in JWT"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Gọi User service và Order service đồng thời
            user_task = client.get(
                f"{USER_SERVICE_URL}/users/{username}"
            )

            order_task = client.get(
                f"{ORDER_SERVICE_URL}/order/{username}"
            )

            user_response, order_response = await asyncio.gather(
                user_task,
                order_task
            )

        # Nếu một service trả lỗi, không trả dashboard thiếu dữ liệu
        user_response.raise_for_status()
        order_response.raise_for_status()

        return {
            "user": user_response.json(),
            "orders": order_response.json()
        }

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="A service timed out while loading dashboard"
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Cannot connect to a service"
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="A service returned an error while loading dashboard"
        ) from exc


import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

# Cấu hình giới hạn
RATE_LIMIT = 10
WINDOW_SECONDS = 1

# Lưu thời điểm gửi request của từng IP
requests_by_ip = defaultdict(deque)


def check_rate_limit(request: Request) -> None:
    client_ip = (
        request.client.host
        if request.client is not None
        else "unknown"
    )

    now = time.monotonic()
    request_times = requests_by_ip[client_ip]

    # Xóa các request đã nằm ngoài cửa sổ 60 giây
    while request_times and now - request_times[0] >= WINDOW_SECONDS:
        request_times.popleft()

    # Từ chối nếu đã đạt giới hạn
    if len(request_times) >= RATE_LIMIT:
        retry_after = max(
            1,
            int(WINDOW_SECONDS - (now - request_times[0]))
        )

        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # Ghi nhận request hiện tại
    request_times.append(now)

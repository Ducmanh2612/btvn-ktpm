# jwt_handler.py
import jwt
import os
from fastapi import HTTPException

SECRET_KEY = os.getenv("SECRET_KEY")

def verify_jwt(request):
    # 1. Lấy header Authorization
    auth_header = request.headers.get("Authorization")

    # 2. Kiểm tra có header không
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu token")

    # 3. Tách lấy token (bỏ chữ "Bearer ")
    token = auth_header.split(" ")[1]

    # 4. Verify token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload   # {"user_id": 123, "exp": ...}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token hết hạn")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
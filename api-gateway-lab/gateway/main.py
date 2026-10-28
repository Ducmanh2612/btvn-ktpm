# main.py (FastAPI)
from fastapi import FastAPI, Request
from jwt_handler import verify_jwt
from rate_limiter import check_rate_limit
from router import forward_to_user, forward_to_order
from dashboard import get_dashboard

app = FastAPI()

@app.get("/dashboard")
async def dashboard(request: Request):
    check_rate_limit(request)
    verify_jwt(request)
    return await get_dashboard(request)   

@app.api_route("/users/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def users(request: Request, path: str):
    check_rate_limit(request)
    verify_jwt(request)
    return await forward_to_user(request, path)   

@app.api_route("/orders/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def orders(request: Request, path: str):
    check_rate_limit(request)
    verify_jwt(request)
    return await forward_to_order(request, path)  

@app.post("/auth/login")                          
async def login(request: Request):
    return await forward_to_user(request, "auth/login")
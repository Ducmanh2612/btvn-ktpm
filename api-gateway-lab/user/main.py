
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from data import create_user, change_password


app = FastAPI()


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    username: str


class MessageResponse(BaseModel):
    message: str


@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
def createUser(user: UserCreate):
    try:
        username = create_user(user.username, user.password)
        return {"username": username}

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc


@app.put(
    "/users/{username}/password",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse
)
def changeUserPassword(username: str, body: PasswordChange):
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must differ from current password"
        )

    success = change_password(
        username,
        body.current_password,
        body.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or current password"
        )

    return {"message": "Password changed successfully"}

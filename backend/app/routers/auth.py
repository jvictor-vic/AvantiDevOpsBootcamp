from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.schemas import LoginRequest, TokenResponse, UserRead
from app.auth.utils import MOCK_USERS, create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    user_data = MOCK_USERS.get(data.email)

    if user_data is None or not verify_password(data.senha, user_data["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user_data["email"]})

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def me(current_user: Annotated[UserRead, Depends(get_current_user)]):
    return current_user

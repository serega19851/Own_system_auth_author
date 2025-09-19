# app/routers/auth.py
from fastapi import APIRouter, Depends, status, Response, Request

from app.dependencies import get_auth_service
from app.schemas.auth import (
    UserRegister, UserRegisterResponse, LoginRequest, TokenResponse,
    RefreshTokenRequest, RefreshTokenResponse
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login_user(
    response: Response,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход в систему"""
    return await auth_service.login_user(login_data, response)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление access токена с помощью refresh токена"""
    return await auth_service.refresh_tokens(request, response, refresh_data)


@router.post("/logout")
async def logout_user(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Выход из системы"""
    return await auth_service.logout_user(response)
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.auth import (
    UserRegister, UserRegisterResponse, LoginRequest, TokenResponse,
    RefreshTokenRequest, RefreshTokenResponse
)
from app.dependencies import get_user_auth_service as get_user_service
from app.services.user.user_auth_service import UserService
from app.auth import get_jwt_service, JWTService, get_cookie_service, CookieService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    user_service: UserService = Depends(get_user_service)
):
    """
    Регистрация нового пользователя
    
    Создает нового пользователя с проверкой:
    - Уникальности email
    - Сложности пароля (минимум 8 символов, буквы + цифры)
    - Совпадения паролей
    - Автоматически назначает роль 'user'
    
    Возвращает информацию о созданном пользователе без пароля.
    """
    try:
        # Создание пользователя через сервис
        new_user = await user_service.create_user(user_data)
        return new_user
        
    except HTTPException:
        # Пробрасываем HTTP исключения (409, 500)
        raise
        
    except Exception as e:
        # Обработка непредвиденных ошибок
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при регистрации пользователя"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    response: Response,
    login_data: LoginRequest,
    user_service: UserService = Depends(get_user_service),
    jwt_service: JWTService = Depends(get_jwt_service),
    cookie_service: CookieService = Depends(get_cookie_service)
):
    """
    Вход в систему
    
    Аутентифицирует пользователя и устанавливает JWT токены в HTTP-only cookies
    с настройками безопасности (Secure, SameSite, HttpOnly).
    """
    # Аутентификация пользователя
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание JWT токенов
    token_data = {"sub": user.email, "user_id": user.id}
    access_token = jwt_service.create_access_token(data=token_data)
    refresh_token = jwt_service.create_refresh_token(data=token_data)
    
    # Получаем настройки для cookies
    cookie_settings = cookie_service.get_cookie_settings()
    refresh_cookie_settings = cookie_service.get_refresh_cookie_settings()
    
    # Устанавливаем HTTP-only cookies с настройками безопасности
    response.set_cookie(
        key="access_token",
        value=access_token,
        **cookie_settings
    )
    
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token,
        **refresh_cookie_settings
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 минут
        user_id=user.id,
        email=user.email
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_data: RefreshTokenRequest,
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_user_service),
    cookie_service: CookieService = Depends(get_cookie_service)
):
    """
    Обновление access токена с помощью refresh токена
    
    Принимает refresh токен (из body или cookie) и возвращает новую пару токенов.
    """
    # Получаем refresh токен из body или из cookie
    refresh_token_value = refresh_data.refresh_token
    if not refresh_token_value:
        refresh_token_value = request.cookies.get("refresh_token")
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем refresh токен
    token_payload = jwt_service.verify_refresh_token(refresh_token_value)
    
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем email и user_id из токена
    email = token_payload.get("sub")
    user_id = token_payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный payload refresh токена",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, что пользователь все еще существует и активен
    user = await user_service.get_user_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем новые токены
    token_data = {"sub": user.email, "user_id": user.id}
    new_access_token = jwt_service.create_access_token(data=token_data)
    new_refresh_token = jwt_service.create_refresh_token(data=token_data)
    
    # Получаем настройки для cookies
    cookie_settings = cookie_service.get_cookie_settings()
    refresh_cookie_settings = cookie_service.get_refresh_cookie_settings()
    
    # Обновляем HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        **cookie_settings
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        **refresh_cookie_settings
    )
    
    return RefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=1800  # 30 минут
    )


@router.post("/logout")
async def logout_user(response: Response):
    """
    Выход из системы
    
    Удаляет HTTP-only cookies с токенами для безопасного выхода.
    """
    # Удаляем cookies с токенами
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # Настроится автоматически в зависимости от окружения
        samesite="lax"
    )
    
    response.delete_cookie(
        key="refresh_token", 
        httponly=True,
        secure=False,  # Настроится автоматически в зависимости от окружения
        samesite="lax"
    )
    
    return {
        "message": "Успешный выход из системы",
        "detail": "HTTP-only cookies с токенами удалены"
    }
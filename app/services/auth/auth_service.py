"""
Сервис аутентификации - координатор всех операций auth домена
"""

from fastapi import HTTPException, status, Response, Request

from app.services.user.user_auth_service import UserService
from app.auth import JWTService, CookieService
from app.schemas.auth import (
    UserRegister, UserRegisterResponse, LoginRequest, TokenResponse,
    RefreshTokenRequest, RefreshTokenResponse
)


class AuthService:
    """
    Координирующий сервис для домена аутентификации
    
    Инкапсулирует всю бизнес-логику аутентификации:
    - Регистрацию пользователей
    - Вход в систему с JWT токенами и cookies
    - Обновление токенов
    - Выход из системы
    """
    
    def __init__(
        self, 
        user_service: UserService,
        jwt_service: JWTService, 
        cookie_service: CookieService
    ):
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.cookie_service = cookie_service
    
    async def register_user(self, user_data: UserRegister) -> UserRegisterResponse:
        """
        Регистрация нового пользователя
        
        Создает нового пользователя с проверкой:
        - Уникальности email
        - Сложности пароля (минимум 8 символов, буквы + цифры)
        - Совпадения паролей
        - Автоматически назначает роль 'user'
        
        Args:
            user_data: Данные для регистрации пользователя
            
        Returns:
            UserRegisterResponse: Информация о созданном пользователе
            
        Raises:
            HTTPException: При ошибках валидации или создания пользователя
        """
        try:
            # Создание пользователя через сервис
            new_user = await self.user_service.create_user(user_data)
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
    
    async def login_user(
        self, 
        login_data: LoginRequest, 
        response: Response
    ) -> TokenResponse:
        """
        Вход в систему
        
        Аутентифицирует пользователя и устанавливает JWT токены в HTTP-only cookies
        с настройками безопасности (Secure, SameSite, HttpOnly).
        
        Args:
            login_data: Email и пароль для входа
            response: HTTP Response для установки cookies
            
        Returns:
            TokenResponse: Токены доступа и информация о пользователе
            
        Raises:
            HTTPException: При неверных учетных данных
        """
        # Аутентификация пользователя
        user = await self.user_service.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создание JWT токенов
        token_data = {"sub": user.email, "user_id": user.id}
        access_token = self.jwt_service.create_access_token(data=token_data)
        refresh_token = self.jwt_service.create_refresh_token(data=token_data)
        
        # Установка cookies с токенами
        self._set_auth_cookies(response, access_token, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30 минут
            user_id=user.id,
            email=user.email
        )
    
    async def refresh_tokens(
        self, 
        request: Request, 
        response: Response, 
        refresh_data: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """
        Обновление access токена с помощью refresh токена
        
        Принимает refresh токен (из body или cookie) и возвращает новую пару токенов.
        
        Args:
            request: HTTP Request для получения cookies
            response: HTTP Response для установки новых cookies
            refresh_data: Данные с refresh токеном
            
        Returns:
            RefreshTokenResponse: Новые токены доступа
            
        Raises:
            HTTPException: При недействительном refresh токене
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
        token_payload = self.jwt_service.verify_refresh_token(refresh_token_value)
        
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
        user = await self.user_service.get_user_by_email(email)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создаем новые токены
        token_data = {"sub": user.email, "user_id": user.id}
        new_access_token = self.jwt_service.create_access_token(data=token_data)
        new_refresh_token = self.jwt_service.create_refresh_token(data=token_data)
        
        # Обновляем cookies с новыми токенами
        self._set_auth_cookies(response, new_access_token, new_refresh_token)
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=1800  # 30 минут
        )
    
    async def logout_user(self, response: Response) -> dict:
        """
        Выход из системы
        
        Удаляет HTTP-only cookies с токенами для безопасного выхода.
        
        Args:
            response: HTTP Response для удаления cookies
            
        Returns:
            dict: Сообщение об успешном выходе
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
    
    def _set_auth_cookies(
        self, 
        response: Response, 
        access_token: str, 
        refresh_token: str
    ) -> None:
        """
        Приватный метод для установки cookies с токенами
        
        Args:
            response: HTTP Response для установки cookies
            access_token: Access токен
            refresh_token: Refresh токен
        """
        # Получаем настройки для cookies
        cookie_settings = self.cookie_service.get_cookie_settings()
        refresh_cookie_settings = self.cookie_service.get_refresh_cookie_settings()
        
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

"""
Сервис аутентификации - координатор всех операций auth домена
"""

from fastapi import Response, Request

from app.services.user.user_auth_service import UserService
from app.auth import JWTService, CookieService
from app.schemas.auth import (
    UserRegister, UserRegisterResponse, LoginRequest, TokenResponse,
    RefreshTokenRequest, RefreshTokenResponse
)
from ..base_service import BaseService
from ...exceptions.auth_exceptions import AuthenticationException
from ...exceptions.business_exceptions import UserException


class AuthService(BaseService):
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
        super().__init__()
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
            
        except UserException:
            # Пробрасываем пользовательские исключения
            raise
            
        except Exception as e:
            # Обработка непредвиденных ошибок
            self._handle_service_error(e, "register_user")
            raise
    
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
        try:
            # Аутентификация пользователя
            user = await self.user_service.authenticate_user(login_data.email, login_data.password)
            
            if not user:
                raise AuthenticationException("Неверный email или пароль", "INVALID_CREDENTIALS")
            
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
        except Exception as e:
            self._handle_service_error(e, "login_user")
            raise
    
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
        try:
            # Получаем refresh токен из body или из cookie
            refresh_token_value = refresh_data.refresh_token
            if not refresh_token_value:
                refresh_token_value = request.cookies.get("refresh_token")
            
            if not refresh_token_value:
                raise AuthenticationException("Refresh токен не предоставлен", "NO_REFRESH_TOKEN")
            
            # Проверяем refresh токен
            token_payload = self.jwt_service.verify_refresh_token(refresh_token_value)
            
            if not token_payload:
                raise AuthenticationException("Недействительный refresh токен", "INVALID_REFRESH_TOKEN")
            
            # Получаем email и user_id из токена
            email = token_payload.get("sub")
            user_id = token_payload.get("user_id")
            
            if not email or not user_id:
                raise AuthenticationException("Недействительный payload refresh токена", "INVALID_TOKEN_PAYLOAD")
            
            # Проверяем, что пользователь все еще существует и активен
            user = await self.user_service.get_user_by_email(email)
            if not user or not user.is_active:
                raise AuthenticationException("Пользователь не найден или неактивен", "USER_INACTIVE_OR_NOT_FOUND")
            
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
        except Exception as e:
            self._handle_service_error(e, "refresh_tokens")
            raise
    
    async def logout_user(self, response: Response) -> dict:
        """
        Выход из системы
        
        Удаляет HTTP-only cookies с токенами для безопасного выхода.
        
        Args:
            response: HTTP Response для удаления cookies
            
        Returns:
            dict: Сообщение об успешном выходе
        """
        try:
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
        except Exception as e:
            self._handle_service_error(e, "logout_user")
            raise
    
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
        try:
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
        except Exception as e:
            self._handle_service_error(e, "_set_auth_cookies")
            raise

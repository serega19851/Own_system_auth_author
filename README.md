# Система аутентификации и авторизации

**Тестовое задание:** Реализация RBAC системы с JWT токенами, ролями и разрешениями.  
**Техническое задание:** [ТЗpython_EM_июль.docx](./ТЗpython_EM_июль.docx)

## Запуск приложения

## Быстрый старт

1. Создать `.env` файл

2. `.env` файл (обязательно заполнить)
```env
DATABASE_URL=postgresql+asyncpg://auth_user:auth_password@postgres:5432/auth_system

# Настройки JWT
SECRET_KEY=your-secret-key-change-in-production
REFRESH_SECRET_KEY=your-refresh-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Настройки безопасности для cookies
ENVIRONMENT=development
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
COOKIE_HTTPONLY=true

# Дополнительные настройки приложения
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

3. Запустить контейнеры:
```bash
docker-compose up --build
```

4. Приложение доступно:
- http://localhost:8000 
- http://localhost:8000/docs

## Тестовые пользователи

При запуске автоматически создаются следующие пользователи:

### 👨‍💼 Администратор
- **Email:** `admin@test.com`
- **Пароль:** `admin123`
- **Возможности:** Полный доступ ко всем ресурсам системы
- **Эндпоинты:**
  - `GET /admin/stats` - статистика системы
  - `GET /admin/users` - список всех пользователей
  - `PUT /admin/users/{id}/roles` - управление ролями пользователей
  - `GET /admin/roles` - список всех ролей
  - `POST /admin/roles` - создание новых ролей
  - `GET /admin/permissions` - список всех разрешений
  - `GET /resources/system/config` - системная конфигурация
  - + все эндпоинты других ролей

### 👤 Обычный пользователь
- **Email:** `user@test.com`
- **Пароль:** `user123`
- **Возможности:** 
  - Чтение документов
  - Просмотр отчетов
  - Просмотр и редактирование собственного профиля
- **Эндпоинты:**
  - `GET /resources/documents` - просмотр документов
  - `GET /resources/reports` - просмотр отчетов
  - `GET /resources/user-profiles` - просмотр профилей
  - `GET /users/me` - получение своего профиля
  - `PUT /users/me` - редактирование своего профиля
  - `DELETE /users/me` - деактивация аккаунта

### 👮‍♀️ Модератор
- **Email:** `moderator@test.com`
- **Пароль:** `moderator123`
- **Возможности:**
  - Создание, редактирование и удаление документов
  - Создание и экспорт отчетов
  - Просмотр профилей пользователей
- **Эндпоинты:**
  - `POST /resources/documents` - создание документов
  - `DELETE /resources/documents/{id}` - удаление документов
  - `POST /resources/reports` - создание отчетов
  - `GET /resources/reports/export` - экспорт отчетов
  - + все эндпоинты обычного пользователя

### 👩‍💼 Менеджер (несколько ролей)
- **Email:** `manager@test.com`
- **Пароль:** `manager123`
- **Возможности:** Объединяет права пользователя и модератора
- **Эндпоинты:** Все эндпоинты пользователя + все эндпоинты модератора

## Аутентификация и работа с токенами

### Общие эндпоинты (для всех)

#### 1. Регистрация `POST /auth/register`
```json
{
  "email": "newuser@test.com",
  "password": "password123",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "middle_name": "Отчество"
}
```

#### 2. Вход в систему `POST /auth/login`
```json
{
  "email": "user@test.com",
  "password": "user123"
}
```
**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### 3. Обновление токена `POST /auth/refresh`
Когда access_token истекает (через 30 минут), используйте refresh_token:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. Выход из системы `POST /auth/logout`
**Удаляет HTTP-only cookies с токенами:**
- Удаляет `access_token` cookie
- Удаляет `refresh_token` cookie  
- Использует `response.delete_cookie()` для полной очистки
- После logout токены становятся недействительными в браузере
- ⚠️ **Примечание:** Работает для фронтенд-приложений, в Swagger UI токены нужно удалять вручную через кнопку "Logout"

### Авторизация в Swagger UI

#### Первоначальная настройка:
1. **Откройте Swagger:** http://localhost:8000/docs
2. **Получите токен через `/auth/login`:**
   - Найдите эндпоинт `POST /auth/login`
   - Нажмите "Try it out"
   - Введите данные пользователя (например: `user@test.com` / `user123`)
   - Нажмите "Execute"
   - **Скопируйте `access_token` из ответа**

3. **Авторизуйтесь в Swagger:**
   - **Нажмите кнопку "Authorize" 🔒** (справа вверху)
   - **Введите токен в формате:** `Bearer your_access_token_here`
   - Пример: `Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
   - **Нажмите "Authorize"** - теперь все запросы будут с токеном

#### Что делать когда токен истекает (через 30 минут):

**Признаки истекшего токена:**
- Получаете ошибку `401 Unauthorized` 
- В ответе сообщение: "Token has expired" или "Invalid token"

**Способы обновления:**

**Способ 1: Через эндпоинт refresh**
1. Найдите эндпоинт `POST /auth/refresh`
2. Нажмите "Try it out" 
3. В body укажите ваш `refresh_token`:
   ```json
   {
     "refresh_token": "ваш_refresh_token_из_первого_логина"
   }
   ```
4. Нажмите "Execute"
5. **Скопируйте новый `access_token`**
6. Снова нажмите "Authorize" 🔒 и обновите токен

**Способ 2: Повторный логин**
1. Снова выполните `POST /auth/login` 
2. Получите новые токены
3. Обновите авторизацию




## Остановка

```bash
docker-compose down
```
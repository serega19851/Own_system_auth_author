#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными
Создает базовые роли, разрешения, ресурсы и пользователей для демонстрации RBAC системы
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import select
from passlib.context import CryptContext

# Импорт моделей и базы данных
from app.database import AsyncSessionLocal
from app.models import User, Role, Permission, Resource

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

# Проверяем нужен ли подробный вывод
VERBOSE_OUTPUT = os.getenv('SEED_VERBOSE', 'false').lower() == 'true'

def log_verbose(message):
    """Выводит сообщение только если включен подробный режим"""
    if VERBOSE_OUTPUT:
        print(message)

async def create_test_data():
    """Создает тестовые данные в базе данных"""
    
    async with AsyncSessionLocal() as session:
        try:
            print("🚀 Создание тестовых данных...")
            
            # ПРОВЕРКА: Если данные уже существуют, пропускаем создание
            result = await session.execute(select(Permission).limit(1))
            existing_permission = result.scalars().first()
            
            if existing_permission:
                print("✅ Тестовые данные уже существуют в базе данных. Пропускаю создание.")
                return
            
            # 1. СОЗДАНИЕ РЕСУРСОВ
            print("📋 Ресурсы...", end=" ")
            resources_data = [
                {"name": "Документы", "resource_type": "documents", "description": "Система документооборота"},
                {"name": "Отчеты", "resource_type": "reports", "description": "Система отчетности"},
                {"name": "Профили пользователей", "resource_type": "user_profiles", "description": "Управление профилями"},
                {"name": "Административная панель", "resource_type": "admin_panel", "description": "Админка системы"},
            ]
            
            resources = []
            for res_data in resources_data:
                resource = Resource(**res_data)
                session.add(resource)
                resources.append(resource)
                log_verbose(f"  ✅ Ресурс: {res_data['name']}")
            print("✅")
            
            await session.flush()  # Получаем ID для ресурсов
            
            # 2. СОЗДАНИЕ РАЗРЕШЕНИЙ
            print("🔐 Разрешения...", end=" ")
            permissions_data = [
                # Разрешения для документов
                {"name": "documents_read", "resource_type": "documents", "action": "read", "description": "Чтение документов"},
                {"name": "documents_write", "resource_type": "documents", "action": "write", "description": "Создание и редактирование документов"},
                {"name": "documents_delete", "resource_type": "documents", "action": "delete", "description": "Удаление документов"},
                
                # Разрешения для отчетов
                {"name": "reports_read", "resource_type": "reports", "action": "read", "description": "Просмотр отчетов"},
                {"name": "reports_create", "resource_type": "reports", "action": "create", "description": "Создание отчетов"},
                {"name": "reports_export", "resource_type": "reports", "action": "export", "description": "Экспорт отчетов"},
                
                # Разрешения для профилей
                {"name": "user_profiles_read", "resource_type": "user_profiles", "action": "read", "description": "Просмотр профилей"},
                {"name": "user_profiles_edit", "resource_type": "user_profiles", "action": "edit", "description": "Редактирование профилей"},
                
                # Административные разрешения
                {"name": "admin_users_manage", "resource_type": "admin_panel", "action": "users_manage", "description": "Управление пользователями"},
                {"name": "admin_roles_manage", "resource_type": "admin_panel", "action": "roles_manage", "description": "Управление ролями"},
                {"name": "admin_system_config", "resource_type": "admin_panel", "action": "system_config", "description": "Настройка системы"},
            ]
            
            permissions = []
            for perm_data in permissions_data:
                permission = Permission(**perm_data)
                session.add(permission)
                permissions.append(permission)
                log_verbose(f"  ✅ Разрешение: {perm_data['name']}")
            print("✅")
            
            await session.flush()  # Получаем ID для разрешений
            
            # 3. СОЗДАНИЕ РОЛЕЙ
            print("👥 Роли...", end=" ")
            
            # Роль: Администратор (все права)
            admin_role = Role(
                name="admin",
                description="Администратор системы - полный доступ ко всем ресурсам",
                is_active=True
            )
            session.add(admin_role)
            await session.flush()
            
            # Роль: Пользователь (базовые права)
            user_role = Role(
                name="user",
                description="Обычный пользователь - базовые права доступа",
                is_active=True
            )
            session.add(user_role)
            
            # Роль: Модератор (управление контентом)
            moderator_role = Role(
                name="moderator",
                description="Модератор - управление документами и отчетами",
                is_active=True
            )
            session.add(moderator_role)
            
            await session.flush()  # Получаем ID для всех ролей
            
            # Связываем роли с разрешениями через прямые запросы
            from sqlalchemy import text
            
            # Админ - все разрешения
            for perm in permissions:
                await session.execute(
                    text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                    {"role_id": admin_role.id, "perm_id": perm.id}
                )
            log_verbose("  ✅ Роль: admin (все разрешения)")
            
            # Пользователь - базовые разрешения
            user_perm_names = ["documents_read", "reports_read", "user_profiles_read", "user_profiles_edit"]
            for perm in permissions:
                if perm.name in user_perm_names:
                    await session.execute(
                        text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                        {"role_id": user_role.id, "perm_id": perm.id}
                    )
            log_verbose("  ✅ Роль: user (базовые разрешения)")
            
            # Модератор - разрешения на управление контентом
            moderator_perm_names = [
                "documents_read", "documents_write", "documents_delete",
                "reports_read", "reports_create", "reports_export", "user_profiles_read"
            ]
            for perm in permissions:
                if perm.name in moderator_perm_names:
                    await session.execute(
                        text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                        {"role_id": moderator_role.id, "perm_id": perm.id}
                    )
            log_verbose("  ✅ Роль: moderator (управление контентом)")
            print("✅")
            
            # 4. СОЗДАНИЕ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ
            print("👤 Пользователи...", end=" ")
            
            # Администратор
            admin_user = User(
                email="admin@test.com",
                password_hash=pwd_context.hash("admin123"),
                first_name="Админ",
                last_name="Системы",
                middle_name="Главный",
                is_active=True
            )
            # Обычный пользователь
            regular_user = User(
                email="user@test.com",
                password_hash=pwd_context.hash("user123"),
                first_name="Иван",
                last_name="Петров",
                middle_name="Сергеевич",
                is_active=True
            )
            session.add(regular_user)
            
            # Модератор
            moderator_user = User(
                email="moderator@test.com",
                password_hash=pwd_context.hash("moderator123"),
                first_name="Анна",
                last_name="Смирнова",
                middle_name="Викторовна",
                is_active=True
            )
            session.add(moderator_user)
            
            # Пользователь с несколькими ролями
            multi_role_user = User(
                email="manager@test.com",
                password_hash=pwd_context.hash("manager123"),
                first_name="Елена",
                last_name="Козлова",
                middle_name="Александровна",
                is_active=True
            )
            session.add(multi_role_user)
            
            # Неактивный пользователь (для демонстрации мягкого удаления)
            inactive_user = User(
                email="deleted@test.com",
                password_hash=pwd_context.hash("deleted123"),
                first_name="Удаленный",
                last_name="Пользователь",
                middle_name="Тестовый",
                is_active=False  # Мягкое удаление
            )
            session.add(inactive_user)
            session.add(admin_user)
            
            await session.flush()  # Получаем ID для всех пользователей
            
            # Назначаем роли пользователям через прямые запросы
            # admin@test.com -> admin
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": admin_user.id, "role_id": admin_role.id}
            )
            log_verbose("  ✅ Пользователь: admin@test.com (роль: admin)")
            
            # user@test.com -> user
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": regular_user.id, "role_id": user_role.id}
            )
            log_verbose("  ✅ Пользователь: user@test.com (роль: user)")
            
            # moderator@test.com -> moderator
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": moderator_user.id, "role_id": moderator_role.id}
            )
            log_verbose("  ✅ Пользователь: moderator@test.com (роль: moderator)")
            
            # manager@test.com -> user + moderator (две роли)
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": multi_role_user.id, "role_id": user_role.id}
            )
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": multi_role_user.id, "role_id": moderator_role.id}
            )
            log_verbose("  ✅ Пользователь: manager@test.com (роли: user, moderator)")
            
            # deleted@test.com -> user (неактивный)
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": inactive_user.id, "role_id": user_role.id}
            )
            log_verbose("  ✅ Пользователь: deleted@test.com (неактивный)")
            print("✅")
            
            # Сохраняем все изменения
            await session.commit()
            print("✅ Тестовые данные созданы успешно!")
            
            if VERBOSE_OUTPUT:
                # Выводим подробную сводку только в verbose режиме
                print("\n📊 СВОДКА СОЗДАННЫХ ДАННЫХ:")
                print(f"  • Ресурсов: {len(resources)}")
                print(f"  • Разрешений: {len(permissions)}")
                print(f"  • Ролей: 3 (admin, user, moderator)")
                print(f"  • Пользователей: 5")
                print("\n🔐 ТЕСТОВЫЕ УЧЕТНЫЕ ЗАПИСИ:")
                print("  • admin@test.com / admin123 (администратор)")
                print("  • user@test.com / user123 (пользователь)")
                print("  • moderator@test.com / moderator123 (модератор)")
                print("  • manager@test.com / manager123 (пользователь + модератор)")
                print("  • deleted@test.com (неактивный)")
            else:
                print("🔐 Готовы тестовые аккаунты: admin@test.com, user@test.com, moderator@test.com")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при создании тестовых данных: {e}")
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    if VERBOSE_OUTPUT:
        print("🎯 Скрипт создания тестовых данных для RBAC системы")
        print("=" * 60)
    asyncio.run(create_test_data())

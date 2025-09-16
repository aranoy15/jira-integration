"""
Сервис для запуска асинхронного Jira клиента
"""

import asyncio
import os
import sys
from lib.async_jira_service import AsyncJiraService


async def main():
    """Основная функция сервиса"""

    # Загружаем секреты из переменных окружения
    secrets = {
        'base_url': os.getenv('JIRA_BASE_URL'),
        'username': os.getenv('JIRA_USERNAME'),
        'api_token': os.getenv('JIRA_API_TOKEN'),
        'auth_type': os.getenv('JIRA_AUTH_TYPE', 'bearer'),
        'password': os.getenv('JIRA_PASSWORD')
    }

    # Проверяем обязательные поля
    required_fields = ['base_url', 'username', 'api_token']
    missing_fields = [field for field in required_fields if not secrets[field]]

    if missing_fields:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_fields)}")
        return

    try:
        async with AsyncJiraService(
            base_url=secrets['base_url'],
            username=secrets['username'],
            api_token=secrets['api_token'],
            password=secrets.get('password'),
            auth_type=secrets.get('auth_type', 'bearer')
        ) as jira:
            print(f"✅ Сервис инициализирован для {secrets['username']}")

            # Получаем информацию о пользователе
            user_info = await jira.get_myself()
            print(f"Пользователь: {user_info.get('displayName', 'N/A')}")

            # Получаем проекты
            projects = await jira.get_projects()
            print(f"Найдено проектов: {len(projects)}")

            # Получаем доски
            boards = await jira.get_boards(max_results=3)
            print(f"Найдено досок: {len(boards)}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())

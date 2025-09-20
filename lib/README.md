# Jira Integration Library

🚀 Полноценная библиотека для работы с Jira API, включающая создание задач, управление спринтами и работу с досками. Поддерживает как синхронный, так и асинхронный режимы работы с использованием aiohttp.

## Структура библиотеки

```
lib/
├── jira_client.py          # Асинхронный клиент для Jira API (thread-safe)
├── jira_provider.py        # Интерфейс и реализации провайдеров данных
├── __init__.py            # Инициализация модуля
└── README.md              # Эта документация
```

## Быстрый старт

### 1. Установка зависимостей

```bash
# Установка основных зависимостей
pip install -r requirements.txt

# Или установка конкретных пакетов
pip install aiohttp>=3.8.0 python-dateutil>=2.8.2 pydantic>=2.0.0 typing-extensions>=4.5.0
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
JIRA_AUTH_TYPE=bearer
```

### 3. Получение API токена

1. Перейдите на https://id.atlassian.com/manage-profile/security/api-tokens
2. Нажмите "Create API token"
3. Введите название токена (например: "Python Jira Client")
4. Скопируйте созданный токен в `.env` файл

### 4. Асинхронное использование (рекомендуется)

```python
import asyncio
import os
from lib.jira_client import JiraClient, JiraIssue

async def main():
    # Создание асинхронного клиента
    client = JiraClient(
        base_url=os.getenv('JIRA_BASE_URL'),
        username=os.getenv('JIRA_USERNAME'),
        api_token=os.getenv('JIRA_API_TOKEN'),
        auth_type=os.getenv('JIRA_AUTH_TYPE', 'bearer')
    )

    # Использование с контекстным менеджером
    async with client:
        # Проверка соединения
        is_connected = await client.test_connection()
        print(f"Соединение: {is_connected}")

        # Получение проектов
        projects = await client.get_projects()
        print(f"Проектов: {len(projects)}")

        # Поиск задач
        issues = await client.search_issues("project = TEST")
        print(f"Задач найдено: {issues.get('total', 0)}")

# Запуск
asyncio.run(main())
```

### 5. Синхронное использование (legacy)

```python
import os
from lib.jira_client import JiraClient

# Создание клиента
client = JiraClient(
    base_url=os.getenv('JIRA_BASE_URL'),
    username=os.getenv('JIRA_USERNAME'),
    api_token=os.getenv('JIRA_API_TOKEN')
)

# Проверка соединения
if client.test_connection():
    client.logger.info("Подключение к Jira успешно")
```

## Основные компоненты

### JiraClient

Thread-safe синхронный клиент для работы с Jira API.

**Особенности:**
- **Thread-safe** - использует `RLock` для безопасной работы из нескольких потоков
- Полная поддержка Jira REST API
- Agile API для работы с досками и спринтами
- Автоматическая обработка ошибок
- Логирование всех операций
- Поддержка различных типов авторизации

**Пример использования:**

```python
from lib.jira_client import JiraClient, JiraIssue

# Создание клиента
client = JiraClient(
    base_url="https://yourcompany.atlassian.net",
    username="your.email@company.com",
    api_token="your_api_token_here"
)

# Создание задачи
issue = JiraIssue(
    project_key="PROJ",
    issue_type="Task",
    summary="Новая задача",
    description="Описание задачи",
    priority="High",
    labels=["python", "api"]
)

issue_key = client.create_issue(issue)
client.logger.info(f"Создана задача: {issue_key}")

# Добавление комментария
client.add_comment(issue_key, "Комментарий к задаче")

# Обновление задачи
client.update_issue(issue_key, {
    "summary": "Обновленное название задачи"
})
```

### JiraProviderBase и JiraJsonProvider

Интерфейс для поставщиков данных и реализация для работы с JSON файлами.

**Особенности:**
- Протокол для различных источников данных
- Поддержка JSON файлов с задачами
- Валидация данных
- Гибкая архитектура для расширения

**Пример использования:**

```python
from lib.jira_provider import JiraJsonProvider

# Создание провайдера
provider = JiraJsonProvider("data/sample_data.json")

# Получение задач
issues = provider.get_issues()
print(f"Получено задач: {len(issues)}")
```

## Основные операции

### Управление задачами

```python
# Создание задачи
issue = JiraIssue(
    project_key="PROJ",
    issue_type="Bug",
    summary="Критическая ошибка",
    description="Описание ошибки",
    priority="Critical",
    assignee="user@example.com",
    labels=["bug", "critical"]
)

issue_key = client.create_issue(issue)

# Получение задачи
issue_info = client.get_issue(issue_key)

# Обновление задачи
client.update_issue(issue_key, {
    "summary": "Исправленное название",
    "priority": "Medium"
})

# Добавление комментария
client.add_comment(issue_key, "Комментарий к задаче")
```

### Поиск задач

```python
# Поиск задач по JQL
jql_queries = [
    "project = PROJ",                                    # Задачи проекта
    "assignee = currentUser()",                         # Мои задачи
    "created >= -7d",                                   # Созданные за неделю
    "priority = High",                                  # Высокий приоритет
    "project = PROJ AND assignee = currentUser()",      # Комбинированный запрос
    "status = 'To Do' AND priority = High"             # Сложный запрос
]

for jql in jql_queries:
    issues = client.search_issues(jql)
    client.logger.info(f"Найдено задач по запросу '{jql}': {len(issues)}")
```

### Agile операции

```python
# Работа с досками
boards = client.get_boards()
client.logger.info(f"Найдено досок: {len(boards)}")

# Получение задач доски
board_issues = client.get_board_issues(board_id=123)

# Получение бэклога
backlog_issues = client.get_board_backlog(board_id=123)

# Создание спринта
sprint = client.create_sprint(
    name="Sprint 1",
    origin_board_id=123,
    start_date="2024-01-01",
    end_date="2024-01-14",
    goal="Цель спринта"
)

# Перемещение задач в спринт
client.move_issues_to_sprint(
    sprint_id=sprint['id'],
    issue_keys=["PROJ-1", "PROJ-2"]
)

# Получение задач спринта
sprint_issues = client.get_sprint_issues(sprint_id=sprint['id'])
```

## Конфигурация

### Типы авторизации

```python
# Bearer токен (рекомендуется)
client = JiraClient(
    base_url="https://yourcompany.atlassian.net",
    username="your.email@company.com",
    api_token="your_api_token_here",
    auth_type="bearer"
)

# Basic авторизация
client = JiraClient(
    base_url="https://yourcompany.atlassian.net",
    username="your.email@company.com",
    password="your_password",
    auth_type="basic"
)
```

### Настройка логирования

```python
import logging

# Настройка уровня логирования
logging.basicConfig(level=logging.INFO)

# Создание клиента с кастомным логгером
client = JiraClient(
    base_url="https://yourcompany.atlassian.net",
    username="your.email@company.com",
    api_token="your_api_token_here"
)

# Клиент автоматически использует logging
client.logger.info("Информационное сообщение")
client.logger.warning("Предупреждение")
client.logger.error("Ошибка")
```

## Расширенные возможности

### Обработка ошибок

```python
try:
    issue_key = client.create_issue(issue)
    client.logger.info(f"Задача создана: {issue_key}")
except Exception as e:
    client.logger.error(f"Ошибка создания задачи: {e}")
    # Клиент автоматически логирует детали ошибки
```

### Пакетные операции

```python
# Создание нескольких задач
issues_data = [
    JiraIssue(project_key="PROJ", issue_type="Task", summary=f"Задача {i}")
    for i in range(1, 6)
]

created_issues = []
for issue in issues_data:
    try:
        issue_key = client.create_issue(issue)
        created_issues.append(issue_key)
    except Exception as e:
        client.logger.error(f"Ошибка создания задачи: {e}")

client.logger.info(f"Создано задач: {len(created_issues)}")
```

## Поддерживаемые операции

### Jira API операции (Синхронные)
- **Создание задач** - полная поддержка всех полей
- **Получение задач** - детальная информация
- **Обновление задач** - изменение любых полей
- **Добавление комментариев** - текстовые комментарии
- **Поиск задач** - полная поддержка JQL
- **Управление проектами** - получение списка проектов
- **Обработка ошибок** - детальное логирование

### Agile API операции
- **Доски (Boards)** - получение и управление
- **Спринты** - создание и управление
- **Бэклог** - получение задач бэклога
- **Перемещение задач** - между спринтами и бэклогом

### Интеграционные возможности
- **Thread-safe операции** - безопасная работа из нескольких потоков
- **Логирование** - структурированные логи
- **Обработка ошибок** - graceful error handling
- **Провайдеры данных** - гибкая система получения данных

## Производительность

### Thread-safe операции

```python
import threading
from lib.jira_client import JiraClient

# Клиент безопасен для использования из нескольких потоков
client = JiraClient(
    base_url="https://yourcompany.atlassian.net",
    username="your.email@company.com",
    api_token="your_api_token"
)

def worker_thread():
    # Каждый поток может безопасно использовать клиент
    issues = client.search_issues("project = PROJ")
    client.logger.info(f"Поток {threading.current_thread().name}: найдено {len(issues)} задач")

# Запуск нескольких потоков
threads = []
for i in range(5):
    t = threading.Thread(target=worker_thread)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Безопасность

### Рекомендации по безопасности

```python
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Использование переменных окружения
client = JiraClient(
    base_url=os.getenv('JIRA_BASE_URL'),
    username=os.getenv('JIRA_USERNAME'),
    api_token=os.getenv('JIRA_API_TOKEN')
)
```

### Лучшие практики

- **Храните токены в переменных окружения**
- **Не коммитьте токены в репозиторий**
- **Используйте HTTPS для подключения**
- **Логируйте все операции для аудита**
- **Используйте Bearer токены вместо паролей**

## Примеры JQL запросов

```python
# Базовые запросы
jql_examples = {
    "Мои задачи": "assignee = currentUser()",
    "Задачи проекта": "project = PROJ",
    "Высокий приоритет": "priority = High",
    "Созданные за неделю": "created >= -7d",
    "Обновленные сегодня": "updated >= startOfDay()",
    "Задачи без исполнителя": "assignee is EMPTY",
    "Задачи с метками": "labels in (bug, urgent)",
    "Задачи определенного типа": "issuetype = Bug",
    "Задачи в спринте": "sprint in openSprints()",
    "Завершенные задачи": "status = Done"
}

# Сложные запросы
complex_jql = {
    "Мои высокоприоритетные задачи": "assignee = currentUser() AND priority = High",
    "Задачи проекта за последний месяц": "project = PROJ AND created >= -30d",
    "Открытые баги": "issuetype = Bug AND status != Done",
    "Задачи с комментариями": "comment is not EMPTY",
    "Задачи с вложениями": "attachments is not EMPTY"
}

# Выполнение запросов
for name, jql in jql_examples.items():
    issues = client.search_issues(jql)
    client.logger.info(f"{name}: {len(issues)} задач")
```

## Устранение неполадок

### Частые проблемы

**Ошибка авторизации:**
```python
# Проверьте правильность токена
if not client.test_connection():
    client.logger.error("Проверьте настройки авторизации")
```

**Ошибка создания задачи:**
```python
try:
    issue_key = client.create_issue(issue)
except Exception as e:
    client.logger.error(f"Ошибка: {e}")
    # Проверьте права доступа к проекту
```

**Проблемы с поиском:**
```python
# Проверьте синтаксис JQL
try:
    issues = client.search_issues("invalid jql")
except Exception as e:
    client.logger.error(f"JQL ошибка: {e}")
```

### Диагностика

```python
# Проверка соединения
if client.test_connection():
    client.logger.info("Соединение с Jira установлено")
else:
    client.logger.error("Ошибка соединения с Jira")

# Проверка доступных проектов
projects = client.get_projects()
client.logger.info(f"Доступно проектов: {len(projects)}")

# Проверка прав пользователя
user_info = client.get_myself()
client.logger.info(f"Пользователь: {user_info.get('displayName')}")
```

## Требования

### Системные требования
- **Python 3.8+** - минимальная версия Python
- **Операционная система** - Linux, macOS, Windows

### Основные зависимости
- **aiohttp >= 3.8.0** - асинхронный HTTP клиент для работы с Jira API
- **python-dateutil >= 2.8.2** - работа с датами и временем
- **pydantic >= 2.0.0** - валидация данных и модели
- **typing-extensions >= 4.5.0** - расширения типизации

### Опциональные зависимости
- **python-dotenv** - для работы с .env файлами
- **requests** - для синхронных HTTP запросов (legacy режим)

## Примеры использования

### JiraClient в JiraIntegration

```python
import asyncio
import os
from lib.jira_client import JiraClient, JiraIssue
from lib.jira_provider import JiraJsonProvider
from service.jira_integration import JiraIntegration

async def main():
    """Пример использования thread-safe JiraClient в асинхронной интеграции"""

    # Настройка переменных окружения
    os.environ['JIRA_BASE_URL'] = 'https://yourcompany.atlassian.net'
    os.environ['JIRA_USERNAME'] = 'your.email@company.com'
    os.environ['JIRA_API_TOKEN'] = 'your_api_token_here'

    # Создание провайдера данных
    jira_provider = JiraJsonProvider('data/sample_data.json')

    # Создание и запуск интеграции
    integration = JiraIntegration(jira_provider=jira_provider)

    try:
        await integration.start()
    except KeyboardInterrupt:
        print("Остановка интеграции...")
        await integration.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

**Архитектура интеграции:**
- **Thread-safe JiraClient** - безопасен для использования из асинхронного кода
- **Асинхронная интеграция** - использует `asyncio` для обработки задач
- **Очередь задач** - `asyncio.Queue` для буферизации
- **Провайдеры данных** - гибкая система получения данных

### JiraJsonProvider - Работа с JSON файлами

```python
from lib.jira_provider import JiraJsonProvider

# Создание провайдера
provider = JiraJsonProvider("data/sample_data.json")

# Получение задач
issues = provider.get_issues()
print(f"Получено задач: {len(issues)}")

# Обработка задач
for issue in issues:
    key = issue.get('key', 'N/A')
    summary = issue.get('fields', {}).get('summary', 'N/A')
    print(f"- {key}: {summary}")
```

### Интеграция с JiraIntegration

```python
from lib.jira_provider import JiraJsonProvider
from service.jira_integration import JiraIntegration
import asyncio

class CustomJiraIntegration:
    def __init__(self):
        self.provider = JiraJsonProvider("data/sample_data.json")
        self.integration = JiraIntegration(self.provider)

    async def start(self):
        # Запуск интеграции
        await self.integration.start()

    async def stop(self):
        # Остановка интеграции
        await self.integration.stop()

# Использование
async def main():
    integration = CustomJiraIntegration()
    try:
        await integration.start()
    except KeyboardInterrupt:
        await integration.stop()

asyncio.run(main())
```

## Дополнительные ресурсы

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Jira Agile API Documentation](https://developer.atlassian.com/cloud/jira/software/rest/)
- [JQL Reference](https://www.atlassian.com/software/jira/guides/expand-jira/jql)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

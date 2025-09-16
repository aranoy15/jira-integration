# Jira Client Library

Полноценная библиотека для работы с Jira API, включающая создание задач, управление спринтами, работу с досками и интеграцию с Kafka.

## 📁 Структура библиотеки

```
lib/
├── jira_client.py          # Основной синхронный клиент для Jira API
├── async_jira_service.py  # Асинхронный сервис для интеграции
├── __init__.py            # Инициализация модуля
└── README.md              # Эта документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
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

### 4. Базовое использование

```python
import os
from jira_client import JiraClient

# Создание клиента
client = JiraClient(
    base_url=os.getenv('JIRA_BASE_URL'),
    username=os.getenv('JIRA_USERNAME'),
    api_token=os.getenv('JIRA_API_TOKEN')
)

# Проверка соединения
if client.test_connection():
    client.logger.info("✅ Подключение к Jira успешно")
```

## 📚 Основные компоненты

### JiraClient

Синхронный клиент для работы с Jira API.

**Особенности:**
- ✅ Полная поддержка Jira REST API
- ✅ Agile API для работы с досками и спринтами
- ✅ Автоматическая обработка ошибок
- ✅ Логирование всех операций
- ✅ Поддержка различных типов авторизации

**Пример использования:**

```python
from jira_client import JiraClient, JiraIssue

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

### AsyncJiraService

Асинхронный сервис для интеграции с другими системами.

**Особенности:**
- ✅ Асинхронная работа с Jira API
- ✅ Интеграция с Kafka для отправки событий
- ✅ Контекстный менеджер для автоматического управления ресурсами
- ✅ Поддержка пакетных операций

**Пример использования:**

```python
import asyncio
from async_jira_service import AsyncJiraService

async def main():
    async with AsyncJiraService(
        base_url="https://yourcompany.atlassian.net",
        username="your.email@company.com",
        api_token="your_api_token_here"
    ) as jira:

        # Получение информации о пользователе
        user_info = await jira.get_myself()
        print(f"Пользователь: {user_info.get('displayName')}")

        # Получение проектов
        projects = await jira.get_projects()
        print(f"Найдено проектов: {len(projects)}")

        # Получение задач
        issues = await jira.search_issues("project = PROJ")
        print(f"Найдено задач: {len(issues)}")

asyncio.run(main())
```

## 🎯 Основные операции

### 📝 Управление задачами

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

# Переход в другое состояние
client.transition_issue(issue_key, "In Progress", "Начинаем работу")
```

### 🔍 Поиск задач

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

### 📋 Agile операции

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

## 🔧 Конфигурация

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

## 🛠️ Расширенные возможности

### Обработка ошибок

```python
try:
    issue_key = client.create_issue(issue)
    client.logger.info(f"✅ Задача создана: {issue_key}")
except Exception as e:
    client.logger.error(f"❌ Ошибка создания задачи: {e}")
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

### Интеграция с Kafka

```python
import asyncio
from async_jira_service import AsyncJiraService

async def sync_jira_to_kafka():
    async with AsyncJiraService(
        base_url=os.getenv('JIRA_BASE_URL'),
        username=os.getenv('JIRA_USERNAME'),
        api_token=os.getenv('JIRA_API_TOKEN')
    ) as jira:

        # Получение задач
        issues = await jira.search_issues("project = PROJ")

        # Отправка в Kafka (если настроен Kafka клиент)
        for issue in issues:
            # Здесь можно добавить отправку в Kafka
            client.logger.info(f"Обработана задача: {issue.get('key')}")

asyncio.run(sync_jira_to_kafka())
```

## 📊 Поддерживаемые операции

### Основные операции
- ✅ **Создание задач** - полная поддержка всех полей
- ✅ **Получение задач** - детальная информация
- ✅ **Обновление задач** - изменение любых полей
- ✅ **Добавление комментариев** - текстовые комментарии
- ✅ **Переходы состояний** - workflow transitions
- ✅ **Поиск задач** - полная поддержка JQL
- ✅ **Управление проектами** - получение списка проектов
- ✅ **Обработка ошибок** - детальное логирование

### Agile API операции
- ✅ **Доски (Boards)** - получение и управление
- ✅ **Спринты** - создание и управление
- ✅ **Бэклог** - получение задач бэклога
- ✅ **Перемещение задач** - между спринтами и бэклогом

### Интеграционные возможности
- ✅ **Асинхронная работа** - для интеграции с другими системами
- ✅ **Контекстные менеджеры** - автоматическое управление ресурсами
- ✅ **Логирование** - структурированные логи
- ✅ **Обработка ошибок** - graceful error handling

## 🔒 Безопасность

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

- 🔐 **Храните токены в переменных окружения**
- 🚫 **Не коммитьте токены в репозиторий**
- 🔒 **Используйте HTTPS для подключения**
- 📝 **Логируйте все операции для аудита**
- 🔄 **Используйте Bearer токены вместо паролей**

## 📋 Примеры JQL запросов

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

## 🆘 Устранение неполадок

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
    client.logger.info("✅ Соединение с Jira установлено")
else:
    client.logger.error("❌ Ошибка соединения с Jira")

# Проверка доступных проектов
projects = client.get_projects()
client.logger.info(f"Доступно проектов: {len(projects)}")

# Проверка прав пользователя
user_info = client.get_myself()
client.logger.info(f"Пользователь: {user_info.get('displayName')}")
```

## 📋 Требования

- Python 3.7+
- requests >= 2.31.0
- python-dateutil >= 2.8.2
- pydantic >= 2.0.0
- typing-extensions >= 4.5.0

## 📚 Дополнительные ресурсы

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Jira Agile API Documentation](https://developer.atlassian.com/cloud/jira/software/rest/)
- [JQL Reference](https://www.atlassian.com/software/jira/guides/expand-jira/jql)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

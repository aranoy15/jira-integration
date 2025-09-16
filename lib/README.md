# Jira Client - Python клиент для работы с Jira API

Полноценный клиент для работы с Jira API, включающий создание задач, добавление комментариев, переходы состояний и поиск.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка

### 1. Получение API токена

1. Перейдите на https://id.atlassian.com/manage-profile/security/api-tokens
2. Нажмите "Create API token"
3. Введите название токена (например: "Python Jira Client")
4. Скопируйте созданный токен

### 2. Настройка клиента

```python
from jira_client import JiraClient

client = JiraClient(
    base_url="https://yourcompany.atlassian.net",  # URL вашего Jira
    username="your.email@company.com",             # Ваш email
    api_token="your_api_token_here"                # API токен
)
```

## Основные функции

### Проверка соединения
```python
if client.test_connection():
    print("✅ Подключение успешно")
```

### Создание задачи
```python
from jira_client import JiraIssue

issue = JiraIssue(
    project_key="PROJ",
    issue_type="Task",
    summary="Название задачи",
    description="Описание задачи",
    priority="High",
    labels=["python", "api"]
)

issue_key = client.create_issue(issue)
print(f"Создана задача: {issue_key}")
```

### Добавление комментария
```python
client.add_comment("PROJ-123", "Текст комментария")
```

### Переход задачи в другое состояние
```python
client.transition_issue("PROJ-123", "In Progress", "Начинаем работу")
```

### Поиск задач
```python
results = client.search_issues("project = PROJ AND assignee = currentUser()")
```

### Получение информации о задаче
```python
issue_info = client.get_issue("PROJ-123")
```

### Agile API функции

#### Работа с досками
```python
# Получение всех досок
boards = client.get_boards()

# Получение досок определенного типа
scrum_boards = client.get_boards(board_type="scrum")

# Получение информации о конкретной доске
board_info = client.get_board(board_id=123)

# Получение задач доски
board_issues = client.get_board_issues(board_id=123)

# Получение бэклога доски
backlog_issues = client.get_board_backlog(board_id=123)
```

#### Работа со спринтами
```python
# Создание спринта
sprint = client.create_sprint(
    name="Sprint 1",
    origin_board_id=123,
    start_date="2024-01-01",
    end_date="2024-01-14",
    goal="Цель спринта"
)

# Получение задач спринта
sprint_issues = client.get_sprint_issues(sprint_id=456)

# Перемещение задач в спринт
client.move_issues_to_sprint(sprint_id=456, issue_keys=["PROJ-1", "PROJ-2"])

# Перемещение задач в бэклог
client.move_issues_to_backlog(issue_keys=["PROJ-1", "PROJ-2"])
```

## Примеры использования

### Базовый пример
```bash
python example_jira_client.py
```

### Agile API функции
```bash
python example_agile_api.py
```

### Интеграция с существующим кодом
```bash
python example_usage.py
```

## Структура файлов

- `jira_client.py` - Основной клиент для работы с Jira API
- `jira_integration.py` - Интеграция с существующим кодом
- `example_jira_client.py` - Примеры использования клиента
- `example_usage.py` - Примеры использования интеграции

## Поддерживаемые операции

### Основные операции
- ✅ Создание задач
- ✅ Получение информации о задачах
- ✅ Обновление задач
- ✅ Добавление комментариев
- ✅ Переходы состояний (transitions)
- ✅ Поиск задач (JQL)
- ✅ Получение списка проектов
- ✅ Получение типов задач
- ✅ Обработка ошибок

### Agile API операции
- ✅ Получение досок (boards)
- ✅ Получение информации о досках
- ✅ Получение задач доски
- ✅ Получение бэклога доски
- ✅ Создание спринтов
- ✅ Получение задач спринта
- ✅ Перемещение задач в спринт
- ✅ Перемещение задач в бэклог

## Обработка ошибок

Клиент автоматически обрабатывает ошибки HTTP запросов и выводит подробную информацию:

```python
try:
    issue_key = client.create_issue(issue)
except Exception as e:
    print(f"Ошибка создания задачи: {e}")
```

## Формат описания задач

Описания задач поддерживают Atlassian Document Format:

```python
description = {
    "type": "doc",
    "version": 1,
    "content": [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Текст описания"
                }
            ]
        }
    ]
}
```

## JQL запросы

Примеры JQL запросов для поиска:

```python
# Задачи проекта PROJ
"project = PROJ"

# Задачи назначенные на текущего пользователя
"assignee = currentUser()"

# Задачи созданные за последние 7 дней
"created >= -7d"

# Задачи с определенным приоритетом
"priority = High"

# Комбинированные запросы
"project = PROJ AND assignee = currentUser() AND priority = High"
```

## Безопасность

- API токены храните в переменных окружения
- Не коммитьте токены в репозиторий
- Используйте HTTPS для подключения к Jira

```python
import os

client = JiraClient(
    base_url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_USERNAME"),
    api_token=os.getenv("JIRA_API_TOKEN")
)
```


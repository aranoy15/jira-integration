# Jira Integration Library

Полноценная библиотека для работы с Jira API, включающая создание задач, управление спринтами и работу с досками. Использует thread-safe синхронный клиент с асинхронной интеграцией.

## 📁 Структура библиотеки

```
lib/
├── jira_client.py          # Основной синхронный клиент для Jira API (thread-safe)
├── jira_provider.py        # Интерфейс и реализации провайдеров данных
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

Thread-safe синхронный клиент для работы с Jira API.

**Особенности:**
- ✅ **Thread-safe** - использует `RLock` для безопасной работы из нескольких потоков
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

### Работа с очередями

```python
import threading
import asyncio
from lib import Queue
from lib.async_queue import AsyncQueue

# Thread-safe очередь
def worker(queue):
    while True:
        try:
            item = queue.get(timeout=1)
            print(f"Обработано: {item}")
            queue.task_done()
        except:
            break

# Создание очереди и запуск worker'ов
queue = Queue()
for i in range(3):
    t = threading.Thread(target=worker, args=(queue,))
    t.start()

# Добавление задач
for i in range(10):
    queue.put(f"задача {i}")

queue.join()  # Ожидание завершения всех задач

# Асинхронная очередь
async def async_worker(queue):
    while not queue.empty():
        item = await queue.get()
        print(f"Асинхронно обработано: {item}")
        await asyncio.sleep(0.1)

async def async_producer(queue):
    for i in range(5):
        await queue.put(f"async задача {i}")
        await asyncio.sleep(0.1)

async def async_example():
    queue = AsyncQueue()

    # Запуск producer и consumer параллельно
    await asyncio.gather(
        async_producer(queue),
        async_worker(queue)
    )

asyncio.run(async_example())
```

### Асинхронная интеграция с очередями

```python
import asyncio
from lib import AsyncJiraClient, JiraIssue

async def jira_to_queue_integration():
    """Интеграция Jira с асинхронной очередью"""

    # Создание компонентов
    jira_client = AsyncJiraClient(
        base_url="https://yourcompany.atlassian.net",
        username="your.email@company.com",
        api_token="your_api_token"
    )

    queue = asyncio.Queue(maxsize=1000)

    async with jira_client:
        # Запуск задач параллельно
        await asyncio.gather(
            jira_poller(jira_client, queue),
            issue_processor(queue),
            return_exceptions=True
        )

async def jira_poller(jira_client, queue):
    """Опрос Jira и добавление задач в очередь"""
    while True:
        try:
            # Получение новых задач
            issues = await jira_client.search_issues(
                "updated >= -1d",
                max_results=50
            )

            # Добавление в очередь
            for issue in issues.get('issues', []):
                await queue.put({
                    'type': 'issue_update',
                    'data': issue,
                    'timestamp': asyncio.get_event_loop().time()
                })

            await asyncio.sleep(60)  # Пауза между опросами

        except Exception as e:
            print(f"Ошибка опроса Jira: {e}")
            await asyncio.sleep(30)

async def issue_processor(queue):
    """Обработка задач из очереди"""
    while True:
        try:
            # Получение задачи из очереди
            item = await asyncio.wait_for(queue.get(), timeout=1.0)

            if item['type'] == 'issue_update':
                issue = item['data']
                print(f"Обрабатываю задачу: {issue['key']}")

                # Здесь ваша логика обработки
                await process_issue(issue)

        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"Ошибка обработки: {e}")

async def process_issue(issue):
    """Обработка одной задачи"""
    # Ваша бизнес-логика
    print(f"Обработана задача: {issue['key']} - {issue['fields']['summary']}")

# Запуск интеграции
asyncio.run(jira_to_queue_integration())
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

### Jira API операции (Синхронные)
- ✅ **Создание задач** - полная поддержка всех полей
- ✅ **Получение задач** - детальная информация
- ✅ **Обновление задач** - изменение любых полей
- ✅ **Добавление комментариев** - текстовые комментарии
- ✅ **Переходы состояний** - workflow transitions
- ✅ **Поиск задач** - полная поддержка JQL
- ✅ **Управление проектами** - получение списка проектов
- ✅ **Обработка ошибок** - детальное логирование

### Jira API операции (Асинхронные)
- ✅ **Асинхронные операции** - все методы с `async/await`
- ✅ **Context manager** - автоматическое управление ресурсами
- ✅ **Concurrent запросы** - ограничение через семафор
- ✅ **Batch операции** - массовое создание задач
- ✅ **Автоматическая пагинация** - получение всех результатов
- ✅ **Высокая производительность** - неблокирующие операции

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

## ⚡ Производительность

### Сравнение синхронного и асинхронного подходов

**Синхронный подход (JiraClient):**
```python
# Последовательное выполнение
for issue_data in issues_data:
    issue_key = client.create_issue(issue_data)  # Блокирующий вызов
    client.add_comment(issue_key, "Комментарий")  # Блокирующий вызов
```

**Асинхронный подход (AsyncJiraClient):**
```python
# Параллельное выполнение
async def create_and_comment(issue_data):
    issue_key = await client.create_issue(issue_data)
    await client.add_comment(issue_key, "Комментарий")
    return issue_key

# Все задачи выполняются параллельно
results = await asyncio.gather(*[
    create_and_comment(issue_data) for issue_data in issues_data
])
```

### Рекомендации по производительности

**Используйте AsyncJiraClient когда:**
- ✅ Нужно обработать много задач (> 10)
- ✅ Интеграция с другими асинхронными системами
- ✅ Требуется высокая пропускная способность
- ✅ Работа с очередями и event-driven архитектурой

**Используйте JiraClient когда:**
- ✅ Простые скрипты и автоматизация
- ✅ Малое количество операций
- ✅ Синхронная архитектура приложения
- ✅ Простота отладки важнее производительности

### Настройка производительности

```python
# Оптимальные настройки для AsyncJiraClient
client = AsyncJiraClient(
    base_url="https://yourcompany.atlassian.net",
    username="your.email@company.com",
    api_token="your_api_token",
    max_concurrent_requests=20,  # Увеличить для мощных серверов
    timeout=60  # Увеличить для медленных сетей
)

# Batch операции для максимальной эффективности
issues_batch = [JiraIssue(...) for _ in range(100)]
created_keys = await client.create_issues_batch(issues_batch)
```

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

### Основные зависимости
- Python 3.7+
- requests >= 2.31.0
- python-dateutil >= 2.8.2
- pydantic >= 2.0.0
- typing-extensions >= 4.5.0

### Для асинхронных операций
- aiohttp >= 3.8.0
- asyncio (встроенный в Python 3.7+)

### Для очередей
- threading (встроенный)
- queue (встроенный)
- asyncio (встроенный)

## 🔧 Примеры использования

### JiraClient в JiraIntegration

```python
import asyncio
import os
from lib import JiraClient, JiraIssue, JiraJsonProvider
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
- ✅ **Thread-safe JiraClient** - безопасен для использования из асинхронного кода
- ✅ **Асинхронная интеграция** - использует `asyncio` для обработки задач
- ✅ **Очередь задач** - `asyncio.Queue` для буферизации
- ✅ **Провайдеры данных** - гибкая система получения данных

### JiraJsonProvider - Мониторинг JSON файла

```python
import asyncio
from lib import JiraJsonProvider

async def on_new_issues(issues):
    """Callback функция для обработки новых задач"""
    print(f"Получены новые задачи: {len(issues)}")
    for issue in issues:
        key = issue.get('key', 'N/A')
        summary = issue.get('fields', {}).get('summary', 'N/A')
        print(f"- {key}: {summary}")

async def main():
    # Создание поставщика с интервалом проверки 2 секунды
    provider = JiraJsonProvider("data/sample_data.json", check_interval=2.0)

    # Запуск мониторинга
    await provider.start_monitoring(on_new_issues)

    # Работаем некоторое время
    await asyncio.sleep(30)

    # Остановка мониторинга
    await provider.stop_monitoring()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
```

### Интеграция с JiraIntegration

```python
from lib import JiraJsonProvider, AsyncJiraClient
import asyncio

class JiraIntegration:
    def __init__(self):
        self.provider = JiraJsonProvider("data/sample_data.json")
        self.jira_client = AsyncJiraClient()
        self.queue = asyncio.Queue()

    async def start(self):
        # Запускаем мониторинг файла
        await self.provider.start_monitoring(self.handle_new_issues)

        # Обрабатываем задачи из очереди
        await self.process_queue()

    async def handle_new_issues(self, issues):
        """Обработка новых задач из файла"""
        for issue in issues:
            await self.queue.put({
                'type': 'issue_update',
                'data': issue
            })

    async def process_queue(self):
        """Обработка очереди задач"""
        while True:
            item = await self.queue.get()
            if item['type'] == 'issue_update':
                await self.jira_client.create_issue(item['data'])
```

## 📚 Дополнительные ресурсы

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Jira Agile API Documentation](https://developer.atlassian.com/cloud/jira/software/rest/)
- [JQL Reference](https://www.atlassian.com/software/jira/guides/expand-jira/jql)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

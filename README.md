# Jira Integration Project

🚀 Полноценная система интеграции с Jira API, включающая thread-safe клиент и асинхронный сервис интеграции.

## 📁 Структура проекта

```
jira-integration/
├── lib/                    # Библиотека для работы с Jira API
│   ├── jira_client.py     # Thread-safe синхронный клиент
│   ├── jira_provider.py   # Провайдеры данных
│   ├── __init__.py        # Инициализация модуля
│   └── README.md          # Документация библиотеки
├── service/               # Сервис интеграции
│   ├── jira_integration.py # Асинхронный сервис
│   └── README.md          # Документация сервиса
├── data/                  # Данные для тестирования
│   └── sample_data.json   # Пример данных задач
├── examples/              # Примеры использования
├── jira_admin/            # Docker конфигурация для администрирования
│   └── docker-compose.yaml
├── temp/                  # Временные файлы
│   └── old_jira_integration.php
├── requirements.txt       # Зависимости проекта
└── README.md              # Эта документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```env
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
JIRA_JSON_FILE_PATH=data/sample_data.json
```

### 3. Запуск сервиса

```bash
python service/jira_integration.py
```

## 🏗️ Архитектура

### Thread-safe JiraClient

- ✅ **RLock** для безопасной работы из нескольких потоков
- ✅ **Полная поддержка Jira REST API**
- ✅ **Agile API** для работы с досками и спринтами
- ✅ **Автоматическая обработка ошибок**

### Асинхронный сервис интеграции

- ✅ **asyncio** для неблокирующих операций
- ✅ **Очередь задач** для буферизации
- ✅ **Провайдеры данных** для гибкого получения данных
- ✅ **Graceful shutdown** по KeyboardInterrupt

### Поток данных

```
JiraJsonProvider -> jira_poller -> asyncio.Queue -> issue_processor -> handle_issue -> JiraClient
```

## 📚 Компоненты

### lib/ - Библиотека

- **JiraClient** - thread-safe синхронный клиент
- **JiraProviderBase** - интерфейс провайдеров данных
- **JiraJsonProvider** - провайдер для JSON файлов

### service/ - Сервис

- **JiraIntegration** - основной сервис интеграции
- **jira_poller** - опрос провайдера данных
- **issue_processor** - обработка задач из очереди
- **handle_issue** - создание задач в Jira

## 🔧 Примеры использования

### Базовое использование JiraClient

```python
from lib import JiraClient, JiraIssue

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
    description="Описание задачи"
)

issue_key = client.create_issue(issue)
print(f"Создана задача: {issue_key}")
```

### Запуск сервиса интеграции

```python
import asyncio
import os
from lib import JiraJsonProvider
from service.jira_integration import JiraIntegration

async def main():
    # Настройка переменных окружения
    os.environ['JIRA_BASE_URL'] = 'https://yourcompany.atlassian.net'
    os.environ['JIRA_USERNAME'] = 'your.email@company.com'
    os.environ['JIRA_API_TOKEN'] = 'your_api_token_here'

    jira_provider = JiraJsonProvider('data/sample_data.json')
    integration = JiraIntegration(jira_provider=jira_provider)

    try:
        await integration.start()
    except KeyboardInterrupt:
        print("Остановка интеграции...")
        await integration.stop()

asyncio.run(main())
```

### Docker развертывание

```bash
# Переход в папку с Docker конфигурацией
cd jira_admin/

# Запуск с docker-compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## 🛠️ Разработка

### Структура данных

```json
{
  "id": "10001",
  "key": "PROJ-1",
  "fields": {
    "summary": "Создать новую задачу",
    "description": "Описание задачи для тестирования",
    "status": {"name": "To Do", "id": "1"},
    "priority": {"name": "High", "id": "1"},
    "assignee": {
      "displayName": "John Doe",
      "emailAddress": "john.doe@example.com"
    }
  }
}
```

### Добавление нового провайдера

```python
from lib.jira_provider import JiraProviderBase

class MyCustomProvider(JiraProviderBase):
    def get_issues(self) -> List[Dict[str, Any]]:
        # Ваша логика получения данных
        return issues
```

## 🚀 Преимущества

- ✅ **Thread-safe** - безопасная работа из нескольких потоков
- ✅ **Асинхронность** - неблокирующие операции с aiohttp
- ✅ **Гибкость** - легко добавить новые провайдеры данных
- ✅ **Надежность** - детальное логирование и обработка ошибок
- ✅ **Простота** - минимум слоев абстракции
- ✅ **Производительность** - эффективная обработка задач
- ✅ **Docker поддержка** - готовые контейнеры для развертывания
- ✅ **Pydantic валидация** - строгая типизация данных

## 📖 Документация

- [lib/README.md](lib/README.md) - Документация библиотеки
- [service/README.md](service/README.md) - Документация сервиса

## 🔧 Требования

### Системные требования
- **Python 3.8+** - минимальная версия Python
- **Операционная система** - Linux, macOS, Windows

### Основные зависимости
- **aiohttp >= 3.8.0** - асинхронный HTTP клиент
- **python-dateutil >= 2.8.2** - работа с датами
- **pydantic >= 2.0.0** - валидация данных
- **typing-extensions >= 4.5.0** - расширения типизации

### Опциональные зависимости
- **python-dotenv** - для работы с .env файлами
- **requests** - для синхронных HTTP запросов (legacy)

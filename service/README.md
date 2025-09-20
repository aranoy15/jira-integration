# Jira Integration Service

Асинхронный сервис для интеграции с Jira API, использующий thread-safe синхронный клиент.

## 📁 Структура сервиса

```
service/
├── jira_integration.py    # Основной сервис интеграции
└── README.md              # Эта документация
```

## 🚀 Архитектура

### JiraIntegration

Основной класс сервиса интеграции с Jira.

**Особенности:**
- ✅ **Thread-safe JiraClient** - использует синхронный клиент с `RLock`
- ✅ **Асинхронная обработка** - `asyncio` для неблокирующих операций
- ✅ **Очередь задач** - `asyncio.Queue` для буферизации
- ✅ **Провайдеры данных** - гибкая система получения данных
- ✅ **Graceful shutdown** - корректная остановка по `KeyboardInterrupt`

**Компоненты:**
- `jira_poller` - опрос провайдера данных
- `issue_processor` - обработка задач из очереди
- `handle_issue` - создание задач в Jira

## 🔧 Использование

### Базовый пример

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

### Переменные окружения

```env
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
JIRA_PASSWORD=your_password (опционально)
JIRA_AUTH_TYPE=bearer (по умолчанию)
JIRA_JSON_FILE_PATH=data/sample_data.json
```

## 🏗️ Архитектура сервиса

### Поток данных

```
JiraJsonProvider -> jira_poller -> asyncio.Queue -> issue_processor -> handle_issue -> JiraClient
```

### Компоненты

#### 1. **jira_poller**
- Опрашивает провайдер данных каждые 60 секунд
- Добавляет задачи в очередь `asyncio.Queue`
- Обрабатывает ошибки провайдера

#### 2. **issue_processor**
- Извлекает задачи из очереди
- Вызывает `handle_issue` для каждой задачи
- Обрабатывает `TimeoutError` и `CancelledError`

#### 3. **handle_issue**
- Получает доступные проекты из Jira
- Определяет тип задачи для проекта
- Создает задачу через `JiraClient`

### Thread Safety

- **JiraClient** использует `RLock` для thread-safe операций
- **Синхронные вызовы** безопасны в асинхронном контексте
- **Нет race conditions** при одновременном доступе

## 🛠️ Отладка

### Логирование

Сервис использует детальное логирование:

```python
# Уровни логирования
logging.info("Starting Jira integration")
logging.info(f"Получено {len(issues)} задач из провайдера")
logging.info(f"Creating issue with data: {issue}")
logging.info(f"Issue created: {issue_key}")

# Обработка ошибок
logging.error(f"Error creating issue: {type(e).__name__}: {e}")
logging.error(f"Traceback: {traceback.format_exc()}")
```

### Мониторинг

- **Queue size** - размер очереди задач
- **Processing status** - статус обработки задач
- **Error tracking** - отслеживание ошибок с полным traceback

## 🚀 Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
export JIRA_BASE_URL="https://yourcompany.atlassian.net"
export JIRA_USERNAME="your.email@company.com"
export JIRA_API_TOKEN="your_api_token_here"

# Запуск сервиса
python service/jira_integration.py
```

## 🔧 Конфигурация

### Настройка провайдера

```python
# JSON файл
jira_provider = JiraJsonProvider('data/sample_data.json')

# Kafka (если реализован)
jira_provider = JiraKafkaProvider('localhost:9092', 'jira-topic')
```

### Настройка очереди

```python
# Размер очереди (по умолчанию 1000)
self.queue = asyncio.Queue(maxsize=1000)
```

### Настройка интервалов

```python
# Интервал опроса провайдера (по умолчанию 60 секунд)
await asyncio.sleep(60)
```

## 🎯 Преимущества архитектуры

- ✅ **Простота** - минимум слоев абстракции
- ✅ **Надежность** - thread-safe операции
- ✅ **Производительность** - асинхронная обработка
- ✅ **Гибкость** - легко добавить новые провайдеры
- ✅ **Отладка** - детальное логирование
- ✅ **Graceful shutdown** - корректная остановка

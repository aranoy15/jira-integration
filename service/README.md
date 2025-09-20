# Jira Integration Service

🚀 Асинхронный сервис для интеграции с Jira API, использующий thread-safe синхронный клиент с поддержкой aiohttp.

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
# Основные настройки Jira
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_api_token_here

# Опциональные настройки
JIRA_PASSWORD=your_password                    # Альтернатива API токену
JIRA_AUTH_TYPE=bearer                          # bearer или basic
JIRA_JSON_FILE_PATH=data/sample_data.json      # Путь к JSON файлу с данными

# Настройки сервиса
JIRA_POLL_INTERVAL=60                          # Интервал опроса в секундах
JIRA_QUEUE_SIZE=1000                          # Размер очереди задач
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
- ✅ **Надежность** - thread-safe операции с RLock
- ✅ **Производительность** - асинхронная обработка с aiohttp
- ✅ **Гибкость** - легко добавить новые провайдеры данных
- ✅ **Отладка** - детальное логирование всех операций
- ✅ **Graceful shutdown** - корректная остановка по KeyboardInterrupt
- ✅ **Масштабируемость** - поддержка больших объемов данных
- ✅ **Мониторинг** - отслеживание состояния очереди и обработки

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

## 📊 Мониторинг и метрики

### Логирование
Сервис предоставляет детальное логирование:
- Статус запуска и остановки
- Количество обработанных задач
- Ошибки и исключения
- Размер очереди задач
- Время обработки

### Метрики производительности
- **Throughput** - количество задач в секунду
- **Latency** - время обработки задачи
- **Queue size** - размер очереди задач
- **Error rate** - процент ошибок обработки
